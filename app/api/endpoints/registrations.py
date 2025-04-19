from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import dependencies
from app.services.points_manager import PointsManager

router = APIRouter()

# Admin dependency for approval endpoints
from fastapi import Request

def get_current_active_admin(current_user: models.User = Depends(dependencies.get_current_user)) -> models.User:
    if not (current_user.is_superuser or getattr(current_user, "user_type", None) == "admin"):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

from fastapi import status
import logging

# This endpoint matches GET /api/v1/registrations (no trailing slash) due to router prefix
@router.get("", response_model=List[schemas.Registration], status_code=status.HTTP_200_OK)
def get_all_registrations(
    *,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(get_current_active_admin),
) -> List[schemas.Registration]:
    """
    Get all registrations (admin only).
    Returns all registration records with user and event info.
    """
    logger = logging.getLogger(__name__)
    try:
        registrations = db.query(models.Registration).all()
        logger.info(f"Admin {current_user.id} fetched all registrations. Count: {len(registrations)}")
        return registrations
    except Exception as e:
        logger.error(f"Failed to fetch registrations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch registrations.")

# Admin dependency for approval endpoints
from fastapi import Request

def get_current_active_admin(current_user: models.User = Depends(dependencies.get_current_user)) -> models.User:
    if not (current_user.is_superuser or getattr(current_user, "user_type", None) == "admin"):
        raise HTTPException(status_code=403, detail="Admin privileges required")
    return current_user

# This is a duplicate endpoint to support both registration patterns
@router.post("/events/{event_id}/register", response_model=schemas.Registration)
def register_for_event_by_path(
    *,
    db: Session = Depends(dependencies.get_db),
    event_id: int = Path(..., gt=0),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """Register current user for an event using path parameter"""
    # Create a registration data object
    registration_data = schemas.RegistrationCreate(event_id=event_id)
    
    # Call the main registration function
    return register_for_event(db=db, registration_data=registration_data, current_user=current_user)


@router.post("/", response_model=schemas.Registration)
def register_for_event(
    *,
    db: Session = Depends(dependencies.get_db),
    registration_data: schemas.RegistrationCreate,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Register current user for an event.
    """
    try:
        # Extract event_id from registration data
        event_id = registration_data.event_id
        
        # Ensure user_id is never null by using current_user.id as fallback
        # This is critical because user_id is a NOT NULL column in the database
        user_id = None
        if hasattr(registration_data, 'user_id') and registration_data.user_id is not None:
            user_id = registration_data.user_id
        else:
            user_id = current_user.id
            
        # Double-check that user_id is not None
        if user_id is None:
            logger.error(f"Critical error: user_id is None when registering for event {event_id}")
            raise HTTPException(status_code=400, detail="User ID is required for registration")
        
        # Set up logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Processing registration for event {event_id} by user {user_id}")
        
        # Check if event exists and is active
        event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.is_active == True).first()
        if not event:
            raise HTTPException(status_code=404, detail="Event not found or inactive")
        
        # Check if event has already started
        from datetime import datetime
        current_time = datetime.utcnow()
        
        if event.start_time <= current_time:
            # Log detailed information about the failed registration attempt
            logger.warning(
                f"Registration rejected for event {event_id} '{event.title}' that started at "
                f"{event.start_time.strftime('%Y-%m-%d %H:%M')}. Current time: {current_time.strftime('%Y-%m-%d %H:%M')}"
            )
            
            # Calculate how long ago the event started
            time_diff = current_time - event.start_time
            hours_ago = time_diff.total_seconds() / 3600
            
            # Provide a more informative error message
            if hours_ago < 1:
                detail = f"This event started {int(time_diff.total_seconds() / 60)} minutes ago. Registration is closed."
            elif hours_ago < 24:
                detail = f"This event started {int(hours_ago)} hours ago. Registration is closed."
            else:
                detail = f"This event started {int(hours_ago / 24)} days ago. Registration is closed."
                
            raise HTTPException(status_code=400, detail=detail)
        
        # Check for existing registration for this user/event
        existing_registration = db.query(models.Registration).filter(
            models.Registration.user_id == user_id,
            models.Registration.event_id == event_id
        ).order_by(models.Registration.id.desc()).first()

        if existing_registration:
            if existing_registration.status in ["pending", "approved"]:
                raise HTTPException(status_code=400, detail="User already registered for this event")
            elif existing_registration.status in ["cancelled", "rejected"]:
                # Allow re-registration by updating the existing record
                existing_registration.status = "pending"
                # Reset payment_status if needed
                if event.price > 0:
                    existing_registration.payment_status = "pending"
                else:
                    existing_registration.payment_status = "not_required"
                db.commit()
                db.refresh(existing_registration)
                return existing_registration
        # Otherwise, create a new registration as before

        # Check if event is at capacity
        if event.max_participants:
            current_registrations = db.query(models.Registration).filter(
                models.Registration.event_id == event_id,
                models.Registration.status != "cancelled"
            ).count()
            
            if current_registrations >= event.max_participants:
                raise HTTPException(status_code=400, detail="Event is at full capacity")
        
        # Create registration
        registration = models.Registration(
            user_id=user_id,
            event_id=event_id,
            status="pending",
            payment_status="pending" if event.price > 0 else "not_required"
        )
        
        db.add(registration)
        db.commit()
        db.refresh(registration)
        
        return registration
    except HTTPException as http_ex:
        # Re-raise HTTP exceptions as they are already properly formatted
        logger.warning(f"HTTP exception during registration: {http_ex.detail}")
        raise
    except Exception as e:
        # Log the exception
        logger.error(f"Unexpected error in register_for_event: {str(e)}")
        # Wrap other exceptions in an HTTPException
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")


from fastapi import Query

@router.get("/events/{event_id}/registrations", response_model=Any)
def get_event_registrations(
    *,
    db: Session = Depends(dependencies.get_db),
    event_id: int = Path(..., gt=0),
    page: int = Query(1, ge=1, description="Page number for pagination"),
    size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get paginated registrations and summary stats for an event (admin/business/superuser only).
    Returns: dict with items, total, approved, attendance_rate, revenue, page, size.
    """
    import logging
    logger = logging.getLogger("event_registrations_debug")
    logger.info(f"[DEBUG] Called get_event_registrations with event_id={event_id}, user_id={current_user.id}, user_type={getattr(current_user, 'user_type', None)}, is_superuser={getattr(current_user, 'is_superuser', None)}")

    # Permission check
    if not (current_user.is_superuser or current_user.user_type in ["admin", "business"]):
        logger.warning(f"[DEBUG] User {current_user.id} lacks permission to view registrations for event {event_id}")
        raise HTTPException(status_code=403, detail="Not enough permissions to view all registrations")

    try:
        # Check if event exists
        event = db.query(models.Event).filter(models.Event.id == event_id).first()
        logger.info(f"[DEBUG] Event query for id={event_id} returned: {event}")
        if not event:
            logger.error(f"[DEBUG] Event not found for id={event_id}")
            raise HTTPException(status_code=404, detail="Event not found")

        # Query registrations for this event
        base_query = db.query(models.Registration).filter(models.Registration.event_id == event_id)
        total = base_query.count()
        approved_count = base_query.filter(models.Registration.status.in_(["approved", "attended", "checked_in"])) .count()
        paid_count = base_query.filter(models.Registration.payment_status == "completed").count()
        revenue = paid_count * (event.price or 0.0)
        attendance_rate = (approved_count / total) if total > 0 else 0.0

        # Pagination
        items = base_query.order_by(models.Registration.registration_date.desc()) \
            .offset((page - 1) * size).limit(size).all()

        # Compose response
        response = {
            "items": [schemas.Registration.from_orm(r) for r in items],
            "total": total,
            "approved": approved_count,
            "attendance_rate": round(attendance_rate * 100, 1),
            "revenue": revenue,
            "page": page,
            "size": size
        }
        logger.info(f"[DEBUG] Returning {len(items)} registrations (page {page}, size {size}) for event_id={event_id}")
        return response
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[ERROR] Exception in get_event_registrations: {str(e)}")
        # DEMO_MODE fallback if enabled
        import os
        if os.getenv("DEMO_MODE", "false").lower() == "true":
            logger.warning("[DEBUG] DEMO_MODE enabled: returning sample data")
            return {
                "items": [],
                "total": 0,
                "approved": 0,
                "attendance_rate": 0.0,
                "revenue": 0.0,
                "page": page,
                "size": size
            }
        raise HTTPException(status_code=500, detail="Failed to fetch event registrations")



@router.get("/users/me/registrations", response_model=List[schemas.Registration])
def get_user_registrations(
    *,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get current user's registrations.
    """
    registrations = db.query(models.Registration).filter(
        models.Registration.user_id == current_user.id
    ).all()
    
    return registrations


@router.delete("/events/{event_id}/register", response_model=schemas.Registration)
def cancel_registration(
    *,
    db: Session = Depends(dependencies.get_db),
    event_id: int = Path(..., gt=0),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Cancel a registration for an event.
    """
    # Find the registration
    registration = db.query(models.Registration).filter(
        models.Registration.user_id == current_user.id,
        models.Registration.event_id == event_id,
        models.Registration.status != "cancelled"
    ).first()
    
    if not registration:
        raise HTTPException(status_code=404, detail="Registration not found")
    
    # Check if event has already started
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    from datetime import datetime, timedelta
    
    # Allow cancellation up to 24 hours before event start
    cancellation_deadline = event.start_time - timedelta(hours=24)
    if datetime.utcnow() > cancellation_deadline:
        raise HTTPException(
            status_code=400, 
            detail="Cannot cancel registration less than 24 hours before event start"
        )
    
    # Update registration status
    registration.status = "cancelled"
    
    db.add(registration)
    db.commit()
    db.refresh(registration)
    
    return registration


@router.post("/events/{event_id}/check-in", response_model=schemas.Registration)
def check_in_user(
    *,
    db: Session = Depends(dependencies.get_db),
    event_id: int = Path(..., gt=0),
    user_id: int,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Check in a user at an event (admin/business only).
    
    This endpoint allows admin or business users to check in attendees at an event.
    It awards points to the user and checks if they qualify for any badges.
    Safeguards are in place to prevent multiple check-ins for the same event.
    """
    # Check if user has admin privileges
    if not (current_user.is_superuser or current_user.user_type in ["admin", "business"]):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to check in users",
        )
    
    # Find the registration
    registration = db.query(models.Registration).filter(
        models.Registration.user_id == user_id,
        models.Registration.event_id == event_id,
        models.Registration.status == "registered"
    ).first()
    
    if not registration:
        # Check if user is already checked in
        existing_checkin = db.query(models.Registration).filter(
            models.Registration.user_id == user_id,
            models.Registration.event_id == event_id,
            models.Registration.status.in_(["attended", "checked_in"])
        ).first()
        
        if existing_checkin:
            raise HTTPException(
                status_code=400, 
                detail=f"User already checked in with status: {existing_checkin.status}"
            )
        else:
            raise HTTPException(status_code=404, detail="Registration not found")
    
    # Check if event is active
    event = db.query(models.Event).filter(
        models.Event.id == event_id,
        models.Event.is_active == True
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found or inactive")
    
    # Check if event is currently ongoing
    from datetime import datetime
    now = datetime.utcnow()
    if not (event.start_time <= now <= event.end_time):
        raise HTTPException(
            status_code=400,
            detail="Can only check in during the event time"
        )
    
    # Update registration status
    registration.status = "checked_in"
    registration.check_in_time = now
    
    db.add(registration)
    db.commit()
    db.refresh(registration)
    
    # Award points to the user
    points_manager = PointsManager(db)
    
    # Award check-in points
    checkin_points = 15  # Base points for checking in
    
    try:
        points_manager.award_points(
            user_id=user_id,
            points=checkin_points,
            transaction_type="earned",
            description=f"Checked in to event: {event.title}",
            event_id=event_id
        )
        
        # Check if the user qualifies for any badges after check-in
        points_manager.check_and_award_badges(user_id)
    except Exception as e:
        # Log the error but don't fail the check-in
        print(f"Error in check-in process: {str(e)}")
    
    return registration


@router.post("/events/{event_id}/self-check-in", response_model=schemas.Registration)
def self_check_in(
    *,
    db: Session = Depends(dependencies.get_db),
    event_id: int = Path(..., gt=0),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Allow a user to check themselves in at an event.
    
    This endpoint allows users to check themselves in at an event they've registered for.
    It awards check-in points and checks if they qualify for any badges.
    Safeguards are in place to prevent multiple check-ins for the same event.
    """
    # Find the user's registration
    registration = db.query(models.Registration).filter(
        models.Registration.user_id == current_user.id,
        models.Registration.event_id == event_id,
        models.Registration.status == "registered"
    ).first()
    
    if not registration:
        # Check if user is already checked in
        existing_checkin = db.query(models.Registration).filter(
            models.Registration.user_id == current_user.id,
            models.Registration.event_id == event_id,
            models.Registration.status.in_(["attended", "checked_in"])
        ).first()
        
        if existing_checkin:
            raise HTTPException(
                status_code=400, 
                detail=f"You are already checked in with status: {existing_checkin.status}"
            )
        else:
            raise HTTPException(status_code=404, detail="Registration not found")
    
    # Check if event is active
    event = db.query(models.Event).filter(
        models.Event.id == event_id,
        models.Event.is_active == True
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found or inactive")
    
    # Check if event is currently ongoing
    from datetime import datetime
    now = datetime.utcnow()
    if not (event.start_time <= now <= event.end_time):
        raise HTTPException(
            status_code=400,
            detail="Can only check in during the event time"
        )
    
    # Update registration status
    registration.status = "checked_in"
    registration.check_in_time = now
    
    db.add(registration)
    db.commit()
    db.refresh(registration)
    
    # Award points to the user
    points_manager = PointsManager(db)
    
    # Award check-in points
    checkin_points = 15  # Base points for checking in
    
    try:
        points_manager.award_points(
            user_id=current_user.id,
            points=checkin_points,
            transaction_type="earned",
            description=f"Checked in to event: {event.title}",
            event_id=event_id
        )
        
        # Check if the user qualifies for any badges after check-in
        points_manager.check_and_award_badges(current_user.id)
    except Exception as e:
        # Log the error but don't fail the check-in
        print(f"Error in self check-in process: {str(e)}")
    
    return registration


@router.post("/events/{event_id}/mark-attendance", response_model=schemas.Registration)
def mark_attendance(
    *,
    db: Session = Depends(dependencies.get_db),
    event_id: int = Path(..., gt=0),
    user_id: int,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Mark a user as having attended an event (admin/business only).
    
    This endpoint should be called after an event has ended to mark users as having attended
    and award them the full event points reward. This is separate from check-in and represents
    final confirmation of attendance.
    """
    # Check if user has admin privileges
    if not (current_user.is_superuser or current_user.user_type in ["admin", "business"]):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to mark attendance",
        )
    
    # Find the registration
    registration = db.query(models.Registration).filter(
        models.Registration.user_id == user_id,
        models.Registration.event_id == event_id,
        models.Registration.status.in_(["registered", "checked_in"])
    ).first()
    
    if not registration:
        # Check if user is already marked as attended
        existing_attendance = db.query(models.Registration).filter(
            models.Registration.user_id == user_id,
            models.Registration.event_id == event_id,
            models.Registration.status == "attended"
        ).first()
        
        if existing_attendance:
            raise HTTPException(
                status_code=400, 
                detail="User already marked as attended"
            )
        else:
            raise HTTPException(status_code=404, detail="Registration not found")
    
    # Check if event exists
    event = db.query(models.Event).filter(
        models.Event.id == event_id
    ).first()
    
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    # Check if event has ended
    from datetime import datetime
    now = datetime.utcnow()
    if now < event.end_time:
        raise HTTPException(
            status_code=400,
            detail="Cannot mark attendance before event has ended"
        )
    
    # Update registration status
    old_status = registration.status
    registration.status = "attended"
    registration.attendance_marked_at = now
    
    db.add(registration)
    db.commit()
    db.refresh(registration)
    
    # Award attendance points
    points_manager = PointsManager(db)
    
    # If user was not checked in, award full points
    # If they were checked in, award the remaining points (event reward minus check-in points)
    if old_status == "registered":
        attendance_points = event.points_reward or 20  # Use event-specific points or default
    else:  # checked_in
        # They already got check-in points, so award the difference
        checkin_points = 15  # Same as in check_in_user
        attendance_points = (event.points_reward or 20) - checkin_points
        if attendance_points < 0:
            attendance_points = 0
    
    try:
        if attendance_points > 0:
            points_manager.award_points(
                user_id=user_id,
                points=attendance_points,
                transaction_type="earned",
                description=f"Attended event: {event.title}",
                event_id=event_id
            )
        
        # Check if the user qualifies for any badges after attendance
        points_manager.check_and_award_badges(user_id)
    except Exception as e:
        # Log the error but don't fail the attendance marking
        print(f"Error in attendance marking process: {str(e)}")
    
    return registration
