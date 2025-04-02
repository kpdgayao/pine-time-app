from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Path
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import dependencies
from app.services.points_manager import PointsManager

router = APIRouter()


@router.post("/events/{event_id}/register", response_model=schemas.Registration)
def register_for_event(
    *,
    db: Session = Depends(dependencies.get_db),
    event_id: int = Path(..., gt=0),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Register current user for an event.
    """
    # Check if event exists and is active
    event = db.query(models.Event).filter(models.Event.id == event_id, models.Event.is_active == True).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found or inactive")
    
    # Check if event has already started
    from datetime import datetime
    if event.start_time <= datetime.utcnow():
        raise HTTPException(status_code=400, detail="Cannot register for an event that has already started")
    
    # Check if user is already registered
    existing_registration = db.query(models.Registration).filter(
        models.Registration.user_id == current_user.id,
        models.Registration.event_id == event_id,
        models.Registration.status != "cancelled"
    ).first()
    
    if existing_registration:
        raise HTTPException(status_code=400, detail="User already registered for this event")
    
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
        user_id=current_user.id,
        event_id=event_id,
        status="registered",
        payment_status="pending" if event.price > 0 else "not_required"
    )
    
    db.add(registration)
    db.commit()
    db.refresh(registration)
    
    return registration


@router.get("/events/{event_id}/registrations", response_model=List[schemas.Registration])
def get_event_registrations(
    *,
    db: Session = Depends(dependencies.get_db),
    event_id: int = Path(..., gt=0),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get all registrations for an event (admin only).
    """
    # Check if user has admin privileges
    if not (current_user.is_superuser or current_user.user_type in ["admin", "business"]):
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions to view all registrations",
        )
    
    # Check if event exists
    event = db.query(models.Event).filter(models.Event.id == event_id).first()
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    
    registrations = db.query(models.Registration).filter(
        models.Registration.event_id == event_id
    ).all()
    
    return registrations


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
