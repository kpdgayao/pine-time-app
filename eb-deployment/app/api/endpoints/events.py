from typing import Any, List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import dependencies
from app.db.session import SessionLocal
from app.services.points_manager import PointsManager

router = APIRouter()

from fastapi import Path
from app.schemas.event import EventStats
from sqlalchemy import func
import logging

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


@router.get("/", response_model=List[schemas.Event])
def read_events(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    event_type: Optional[str] = None,
    upcoming: Optional[bool] = None,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
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
