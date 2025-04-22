from typing import Any, List, Optional, Dict
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import dependencies
from app.api.dependencies import safe_api_call, safe_api_response_handler, safe_get_user_id
from app.db.session import SessionLocal
from app.services.points_manager import PointsManager
from sqlalchemy.exc import SQLAlchemyError

router = APIRouter()

from fastapi import Path
from app.schemas.event import EventStats
from sqlalchemy import func
import logging

@router.get("/recommended", response_model=List[schemas.Event])
def get_recommended_events(
    request: Request,
    db: Session = Depends(dependencies.get_db),
    limit: int = Query(5, ge=1, le=20),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get personalized event recommendations for the current user.
    
    Recommendations are based on:
    1. User's past event attendance
    2. User's interests (event types)
    3. User's location
    4. Popularity of events
    5. Upcoming events
    """
    try:
        # Get user ID safely
        user_id = getattr(current_user, "id", None)
        if user_id is None:
            logging.warning("User ID is None when fetching recommended events")
            return []
        
        logging.info(f"Generating event recommendations for user {user_id}")
        
        # Get current date for filtering upcoming events
        current_date = datetime.now()
        
        # 1. Find event types the user has previously attended
        user_attended_event_types = []
        try:
            # Get past registrations
            past_registrations = db.query(models.Registration).filter(
                models.Registration.user_id == user_id,
                models.Registration.status.in_(["confirmed", "attended"])
            ).all()
            
            # Get event types from these registrations
            for reg in past_registrations:
                event = db.query(models.Event).filter(models.Event.id == reg.event_id).first()
                if event and event.event_type and event.event_type not in user_attended_event_types:
                    user_attended_event_types.append(event.event_type)
        except Exception as e:
            logging.error(f"Error getting user's attended event types: {str(e)}")
        
        # 2. Get user's location if available
        user_location = None
        try:
            # Check if UserProfile model exists in the models module
            if hasattr(models, 'UserProfile'):
                user_profile = db.query(models.UserProfile).filter(models.UserProfile.user_id == user_id).first()
                if user_profile:
                    user_location = user_profile.location
            else:
                # Try to get location from User model directly if available
                user = db.query(models.User).filter(models.User.id == user_id).first()
                if user and hasattr(user, 'location'):
                    user_location = user.location
        except Exception as e:
            logging.error(f"Error getting user's location: {str(e)}")
        
        # 3. Build recommendation query
        query = db.query(models.Event).filter(
            models.Event.is_active == True,
            models.Event.start_time > current_date  # Only upcoming events
        )
        
        # If we have user's preferred event types, prioritize those
        recommended_events = []
        if user_attended_event_types:
            # First get events matching user's interests
            type_matched_events = query.filter(models.Event.event_type.in_(user_attended_event_types))\
                .order_by(models.Event.start_time.asc())\
                .limit(limit).all()
            recommended_events.extend(type_matched_events)
        
        # If we don't have enough recommendations yet, add popular events
        if len(recommended_events) < limit:
            remaining_limit = limit - len(recommended_events)
            
            # Get event IDs we already recommended to avoid duplicates
            existing_event_ids = [event.id for event in recommended_events]
            
            # Get popular events (most registrations) that aren't already recommended
            popular_events_query = db.query(models.Event)\
                .outerjoin(models.Registration, models.Event.id == models.Registration.event_id)\
                .filter(
                    models.Event.is_active == True,
                    models.Event.start_time > current_date
                )
            
            if existing_event_ids:
                popular_events_query = popular_events_query.filter(~models.Event.id.in_(existing_event_ids))
                
            popular_events = popular_events_query\
                .group_by(models.Event.id)\
                .order_by(func.count(models.Registration.id).desc())\
                .limit(remaining_limit).all()
                
            recommended_events.extend(popular_events)
        
        # If we still don't have enough, add some random upcoming events
        if len(recommended_events) < limit:
            remaining_limit = limit - len(recommended_events)
            
            # Get event IDs we already recommended to avoid duplicates
            existing_event_ids = [event.id for event in recommended_events]
            
            # Get random upcoming events that aren't already recommended
            random_events_query = db.query(models.Event).filter(
                models.Event.is_active == True,
                models.Event.start_time > current_date
            )
            
            if existing_event_ids:
                random_events_query = random_events_query.filter(~models.Event.id.in_(existing_event_ids))
                
            random_events = random_events_query.order_by(func.random()).limit(remaining_limit).all()
            recommended_events.extend(random_events)
        
        logging.info(f"Generated {len(recommended_events)} event recommendations for user {user_id}")
        return recommended_events
        
    except Exception as e:
        logging.error(f"Error generating event recommendations: {str(e)}", exc_info=True)
        # Return empty list as fallback
        return []


@router.get("/{event_id}/stats", response_model=EventStats)
def get_event_stats(
    *,
    db: Session = Depends(dependencies.get_db),
    event_id: int = Path(..., gt=0),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get statistics for a specific event: registration count, total revenue, unique participants, etc.
    """
    logger = logging.getLogger("events.stats")
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        logger.warning(f"Event stats requested for nonexistent event_id={event_id}")
        raise HTTPException(status_code=404, detail="Event not found")

    # Only admins/business can see stats for inactive events
    if not event.is_active and not (current_user.is_superuser or current_user.user_type in ["admin", "business"]):
        logger.warning(f"Unauthorized stats access for inactive event_id={event_id} by user_id={current_user.id}")
        raise HTTPException(status_code=403, detail="Not enough permissions to view stats for inactive event")

    try:
        registration_count = db.query(func.count(models.Registration.id)).filter(models.Registration.event_id == event_id).scalar() or 0
        completed_count = db.query(func.count(models.Registration.id)).filter(
            models.Registration.event_id == event_id,
            models.Registration.payment_status == 'completed'
        ).scalar() or 0
        total_revenue = completed_count * (event.price or 0.0)
        unique_participants = db.query(func.count(func.distinct(models.Registration.user_id))).filter(models.Registration.event_id == event_id).scalar() or 0
    except Exception as e:
        logger.error(f"DB error while fetching stats for event_id={event_id}: {e}")
        raise HTTPException(status_code=500, detail="Database error while fetching event stats")

    return EventStats(
        event_id=event_id,
        registration_count=registration_count,
        total_revenue=total_revenue,
        unique_participants=unique_participants
    )


from fastapi import Request

@router.get("/", response_model=List[schemas.Event])
def read_events(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[str] = None,
    upcoming: Optional[bool] = None,
    request: Request = None,
) -> Any:
    """
    Retrieve events with filtering options. Public for GET. Authenticated users see all, unauthenticated see only active events.
    """
    query = db.query(models.Event)

    # Apply filters
    if event_type:
        query = query.filter(models.Event.event_type == event_type)

    if upcoming is not None:
        now = datetime.utcnow()
        if upcoming:
            query = query.filter(models.Event.start_time > now)
        else:  # past events
            query = query.filter(models.Event.end_time < now)

    # Try to get user from Authorization header (optional)
    user = None
    try:
        from app.api.dependencies import get_current_user
        token = None
        if request and "authorization" in request.headers:
            token = request.headers["authorization"].replace("Bearer ", "")
        if token:
            user = get_current_user.__wrapped__(db, token)  # bypass Depends
    except Exception:
        user = None

    # Only show active events to unauthenticated users
    if not user or (not getattr(user, 'is_superuser', False) and getattr(user, 'user_type', None) != "admin"):
        query = query.filter(models.Event.is_active == True)

    # Order by start_time
    query = query.order_by(models.Event.start_time)

    events = query.offset(skip).limit(limit).all()
    return events

    """
    Retrieve events with filtering options.
    """
    query = db.query(models.Event)
    
    # Apply filters
    if event_type:
        query = query.filter(models.Event.event_type == event_type)
        
    if upcoming is not None:
        now = datetime.utcnow()
        if upcoming:
            query = query.filter(models.Event.start_time > now)
        else:  # past events
            query = query.filter(models.Event.end_time < now)
    
    # Only show active events to regular users
    if not current_user.is_superuser and current_user.user_type != "admin":
        query = query.filter(models.Event.is_active == True)
    
    # Order by start_time
    query = query.order_by(models.Event.start_time)
    
    events = query.offset(skip).limit(limit).all()
    return events


@router.get("/{event_id}", response_model=schemas.Event)
def read_event(
    *,
    db: Session = Depends(dependencies.get_db),
    event_id: int,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get event by ID.
    """
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if event is active or user has admin privileges
    if not event.is_active and not (current_user.is_superuser or current_user.user_type == "admin"):
        raise HTTPException(status_code=404, detail="Event not found")
    
    return event


@router.post("/", response_model=schemas.Event)
def create_event(
    *,
    db: Session = Depends(dependencies.get_db),
    event_in: schemas.EventCreate,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Create new event.
    
    Creates a new event and awards points to the host for creating it.
    Only business and admin users can create events.
    """
    # Check if user has permission to create events
    if not (current_user.is_superuser or current_user.user_type in ["admin", "business"]):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to create events",
        )
    
    # Validate event dates
    if event_in.end_time <= event_in.start_time:
        raise HTTPException(
            status_code=400,
            detail="End time must be after start time",
        )
    
    event = models.Event(
        title=event_in.title,
        description=event_in.description,
        event_type=event_in.event_type,
        location=event_in.location,
        start_time=event_in.start_time,
        end_time=event_in.end_time,
        max_participants=event_in.max_participants,
        points_reward=event_in.points_reward,
        is_active=event_in.is_active,
        image_url=event_in.image_url,
        price=event_in.price,
    )
    db.add(event)
    db.commit()
    db.refresh(event)
    
    # Award points to the host for creating an event
    points_manager = PointsManager(db)
    host_points = 50  # Points awarded for hosting an event
    
    try:
        points_manager.award_points(
            user_id=current_user.id,
            points=host_points,
            transaction_type="earned",
            description=f"Created event: {event.title}",
            event_id=event.id
        )
    except Exception as e:
        # Log the error but don't fail the event creation
        print(f"Error awarding host points: {str(e)}")
    
    return event


@router.put("/{event_id}", response_model=schemas.Event)
def update_event(
    *,
    db: Session = Depends(dependencies.get_db),
    event_id: int,
    event_in: schemas.EventUpdate,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Update an event.
    """
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if user has permission to update events
    if not (current_user.is_superuser or current_user.user_type in ["admin", "business"]):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to update events",
        )
    
    # Update event attributes
    update_data = event_in.dict(exclude_unset=True)
    
    # Validate event dates if both are provided
    if update_data.get("start_time") and update_data.get("end_time"):
        if update_data["end_time"] <= update_data["start_time"]:
            raise HTTPException(
                status_code=400,
                detail="End time must be after start time",
            )
    
    for field, value in update_data.items():
        setattr(event, field, value)
    
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.delete("/{event_id}", response_model=schemas.Event)
def delete_event(
    *,
    db: Session = Depends(dependencies.get_db),
    event_id: int,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Cancel an event (soft delete).
    """
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if user has permission to delete events
    if not (current_user.is_superuser or current_user.user_type in ["admin", "business"]):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to cancel events",
        )
    
    # Soft delete by setting is_active to False
    event.is_active = False
    db.add(event)
    db.commit()
    db.refresh(event)
    return event


@router.post("/{event_id}/register", response_model=schemas.Registration)
def register_for_event_path(
    *,
    db: Session = Depends(dependencies.get_db),
    event_id: int,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Register current user for an event.
    This endpoint is a redirect to the main registration endpoint in the registrations router.
    """
    try:
        # Import the registration function from registrations module
        from app.api.endpoints.registrations import register_for_event
        
        # Create a registration data object with explicit user_id
        registration_data = schemas.RegistrationCreate(event_id=event_id, user_id=current_user.id)
        
        # Call the main registration function
        return register_for_event(db=db, registration_data=registration_data, current_user=current_user)
    except Exception as e:
        # Log the exception
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error in register_for_event_path: {str(e)}")
        
        # Check if it's already an HTTPException
        if isinstance(e, HTTPException):
            raise e
        
        # Otherwise, wrap it in an HTTPException
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")


@router.post("/{event_id}/complete", response_model=schemas.Event)
def complete_event(
    *,
    db: Session = Depends(dependencies.get_db),
    event_id: int,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Mark an event as completed and award final points.
    
    This endpoint should be called after an event has ended to:
    1. Mark the event as completed
    2. Award any final bonus points to attendees
    3. Award host completion points
    
    Only admin and business users can complete events.
    """
    # Check if user has permission to complete events
    if not (current_user.is_superuser or current_user.user_type in ["admin", "business"]):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to complete events",
        )
    
    # Get the event
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if event has already ended
    now = datetime.utcnow()
    if event.end_time > now:
        raise HTTPException(
            status_code=400,
            detail="Cannot complete an event that hasn't ended yet"
        )
    
    # Check if event is already completed
    if not event.is_active:
        raise HTTPException(
            status_code=400,
            detail="Event is already completed or cancelled"
        )
    
    # Get all attendees
    attendees = db.query(models.Registration).filter(
        models.Registration.event_id == event_id,
        models.Registration.status == "attended"
    ).all()
    
    # Award completion bonus points to all attendees
    points_manager = PointsManager(db)
    completion_bonus = 10  # Bonus points for event completion
    
    for attendee in attendees:
        try:
            points_manager.award_points(
                user_id=attendee.user_id,
                points=completion_bonus,
                transaction_type="earned",
                description=f"Completion bonus for event: {event.title}",
                event_id=event_id
            )
        except Exception as e:
            # Log the error but continue with other attendees
            print(f"Error awarding completion bonus: {str(e)}")
    
    # Award host completion points
    host_completion_points = 25  # Points for successfully completing an event
    try:
        points_manager.award_points(
            user_id=current_user.id,
            points=host_completion_points,
            transaction_type="earned",
            description=f"Completed hosting event: {event.title}",
            event_id=event_id
        )
    except Exception as e:
        # Log the error but don't fail the event completion
        print(f"Error awarding host completion points: {str(e)}")
    
    # Mark event as completed (inactive)
    event.is_active = False
    db.add(event)
    db.commit()
    db.refresh(event)
    
    return event
