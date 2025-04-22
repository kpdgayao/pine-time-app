from typing import Any, List, Dict, Optional

from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
from fastapi.encoders import jsonable_encoder
from pydantic import EmailStr
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app import models, schemas
from app.api import dependencies
from app.core.security import get_password_hash, verify_password
from app.services.points_manager import PointsManager
from app.services.badge_manager import BadgeManager
from datetime import datetime, timedelta
import random

router = APIRouter()


@router.get("/", response_model=List[schemas.User])
def read_users(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Retrieve users.
    """
    users = db.query(models.User).offset(skip).limit(limit).all()
    return users


@router.post("/", response_model=schemas.User)
def create_user(
    *,
    db: Session = Depends(dependencies.get_db),
    user_in: schemas.UserCreate,
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Create new user.
    """
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = db.query(models.User).filter(models.User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user_in_data = user_in.dict()
    user_in_data.pop("password")
    user = models.User(**user_in_data)
    user.hashed_password = get_password_hash(user_in.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# --- NEW USER MANAGEMENT ENDPOINTS ---
from fastapi import status, Request
import logging
from typing import List, Dict, Any
from app.api.dependencies import safe_api_call, safe_api_response_handler, safe_get_user_id
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta


@router.put("/me", response_model=schemas.User)
def update_user_me(
    *,
    db: Session = Depends(dependencies.get_db),
    password: str = Body(None),
    full_name: str = Body(None),
    email: EmailStr = Body(None),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Update own user.
    """
    current_user_data = jsonable_encoder(current_user)
    user_in = schemas.UserUpdate(**current_user_data)
    if password is not None:
        user_in.password = password
    if full_name is not None:
        user_in.full_name = full_name
    if email is not None:
        user_in.email = email
    user = current_user
    if password is not None:
        user.hashed_password = get_password_hash(password)
    if full_name is not None:
        user.full_name = full_name
    if email is not None:
        user.email = email
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# --- NEW USER MANAGEMENT ENDPOINTS ---
from fastapi import status, Request
import logging
from typing import List, Dict, Any
from app.api.dependencies import safe_api_call, safe_api_response_handler, safe_get_user_id
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta


@router.get("/me", response_model=schemas.User)
def read_user_me(
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get current user.
    """
    return current_user


@router.get("/{user_id}", response_model=schemas.User)
def read_user_by_id(
    user_id: int,
    current_user: models.User = Depends(dependencies.get_current_active_user),
    db: Session = Depends(dependencies.get_db),
) -> Any:
    """
    Get a specific user by id.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user == current_user:
        return user
    if current_user.is_superuser:
        return user
    raise HTTPException(
        status_code=400, detail="The user doesn't have enough privileges"
    )

# --- NEW USER MANAGEMENT ENDPOINTS ---
from fastapi import status, Request
import logging
from typing import List, Dict, Any
from app.api.dependencies import safe_api_call, safe_api_response_handler, safe_get_user_id
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta


@router.put("/{user_id}", response_model=schemas.User)
def update_user(
    *,
    db: Session = Depends(dependencies.get_db),
    user_id: int,
    user_in: schemas.UserUpdate,
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Update a user.
    """
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=404,
            detail="The user with this id does not exist in the system",
        )
    user_data = jsonable_encoder(user)
    update_data = user_in.dict(exclude_unset=True)
    for field in user_data:
        if field in update_data:
            setattr(user, field, update_data[field])
    if user_in.password:
        user.hashed_password = get_password_hash(user_in.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

# --- NEW USER MANAGEMENT ENDPOINTS ---
from fastapi import status, Request
import logging
from typing import List, Dict, Any
from app.api.dependencies import safe_api_call, safe_api_response_handler, safe_get_user_id
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime, timedelta


@router.post("/register", response_model=schemas.User)
def register_user(
    *,
    db: Session = Depends(dependencies.get_db),
    user_in: schemas.UserCreate,
) -> Any:
    """
    Register new user without requiring superuser privileges.
    """
    user = db.query(models.User).filter(models.User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    user = db.query(models.User).filter(models.User.username == user_in.username).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user_in_data = user_in.dict()
    user_in_data.pop("password")
    # Set default role to regular user
    user_in_data["is_superuser"] = False
    user_in_data["is_active"] = True
    user = models.User(**user_in_data)
    user.hashed_password = get_password_hash(user_in.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}/activities", response_model=List[Dict])
@safe_api_call
def get_user_activities(
    request: Request,
    user_id: int,
    db: Session = Depends(dependencies.get_db),
    limit: int = 10,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get a user's recent activities.
    
    Returns a comprehensive list of recent activities including:
    - Points transactions
    - Event registrations
    - Badge earnings
    
    Regular users can only view their own activities, while admins can view any user's activities.
    """
    try:
        # Check permissions - users can only view their own activities unless they're admins
        current_user_id = safe_get_user_id(current_user)
        if current_user_id is None:
            logging.warning(f"User ID is None when fetching activities for user {user_id}")
            raise HTTPException(status_code=401, detail="Authentication required")
            
        if current_user_id != user_id and not (current_user.is_superuser or current_user.user_type == "admin"):
            logging.warning(f"User {current_user_id} attempted to access activities for user {user_id}")
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        activities = []
        
        try:
            # Get points transactions
            points_transactions = db.query(models.PointsTransaction).filter(
                models.PointsTransaction.user_id == user_id
            ).order_by(models.PointsTransaction.transaction_date.desc()).limit(limit).all()
            
            for tx in points_transactions:
                # Get associated event information if available
                event_info = None
                if tx.event_id:
                    try:
                        event = db.query(models.Event).filter(models.Event.id == tx.event_id).first()
                        if event:
                            event_info = {
                                "id": event.id,
                                "title": event.title,
                                "event_type": event.event_type
                            }
                    except Exception as event_error:
                        logging.error(f"Error getting event info for transaction {tx.id}: {str(event_error)}")
                
                activity = {
                    "id": f"points_{tx.id}",
                    "type": "points",
                    "subtype": tx.transaction_type,
                    "points": tx.points,
                    "description": tx.description,
                    "timestamp": tx.transaction_date.isoformat() if tx.transaction_date else None,
                    "event": event_info
                }
                activities.append(activity)
            
            # Get event registrations
            try:
                registrations = db.query(models.Registration).filter(
                    models.Registration.user_id == user_id
                ).order_by(models.Registration.registration_date.desc()).limit(limit).all()
                
                for reg in registrations:
                    event_info = None
                    try:
                        event = db.query(models.Event).filter(models.Event.id == reg.event_id).first()
                        if event:
                            event_info = {
                                "id": event.id,
                                "title": event.title,
                                "event_type": event.event_type,
                                "start_time": event.start_time.isoformat() if event.start_time else None
                            }
                    except Exception as event_error:
                        logging.error(f"Error getting event info for registration {reg.id}: {str(event_error)}")
                    
                    activity = {
                        "id": f"registration_{reg.id}",
                        "type": "registration",
                        "subtype": reg.status,
                        "description": f"Registered for {event_info['title'] if event_info else 'an event'}",
                        "timestamp": reg.registration_date.isoformat() if reg.registration_date else None,
                        "event": event_info
                    }
                    activities.append(activity)
            except Exception as reg_error:
                logging.error(f"Error getting registrations for user {user_id}: {str(reg_error)}")
            
            # Get badge earnings
            try:
                user_badges = db.query(models.UserBadge).filter(
                    models.UserBadge.user_id == user_id
                ).order_by(models.UserBadge.earned_date.desc()).limit(limit).all()
                
                for user_badge in user_badges:
                    badge_info = None
                    try:
                        badge = db.query(models.Badge).filter(models.Badge.id == user_badge.badge_id).first()
                        if badge:
                            badge_info = {
                                "id": badge.id,
                                "name": badge.name,
                                "description": badge.description,
                                "icon_url": badge.icon_url if hasattr(badge, 'icon_url') else None
                            }
                    except Exception as badge_error:
                        logging.error(f"Error getting badge info for user badge {user_badge.id}: {str(badge_error)}")
                    
                    activity = {
                        "id": f"badge_{user_badge.id}",
                        "type": "badge",
                        "subtype": "earned",
                        "description": f"Earned the {badge_info['name'] if badge_info else 'a badge'} badge",
                        "timestamp": user_badge.earned_date.isoformat() if hasattr(user_badge, 'earned_date') and user_badge.earned_date else None,
                        "badge": badge_info,
                        "level": user_badge.level if hasattr(user_badge, 'level') else 1
                    }
                    activities.append(activity)
            except Exception as badge_error:
                logging.error(f"Error getting badges for user {user_id}: {str(badge_error)}")
            
            # Sort all activities by timestamp (most recent first)
            activities.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            
            # Limit to requested number
            activities = activities[:limit]
            
            logging.info(f"Retrieved {len(activities)} activities for user {user_id}")
            return activities
            
        except SQLAlchemyError as db_error:
            logging.error(f"Database error in get_user_activities: {str(db_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred when retrieving user activities"
            )
            
    except Exception as e:
        logging.error(f"Unexpected error in get_user_activities: {str(e)}", exc_info=True)
        # Return empty list as fallback with graceful degradation
        return []


@router.get("/{user_id}/events", response_model=List[Dict])
@safe_api_call
def get_user_events(
    request: Request,
    user_id: int,
    db: Session = Depends(dependencies.get_db),
    status: Optional[str] = Query(None, description="Filter by event status: upcoming, past, all"),
    limit: int = Query(10, ge=1, le=50),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get events that a specific user has registered for.
    
    Returns a list of events with registration status and details.
    Regular users can only view their own events, while admins can view any user's events.
    """
    try:
        # Check permissions - users can only view their own events unless they're admins
        current_user_id = safe_get_user_id(current_user)
        if current_user_id is None:
            logging.warning(f"User ID is None when fetching events for user {user_id}")
            raise HTTPException(status_code=401, detail="Authentication required")
            
        if current_user_id != user_id and not (current_user.is_superuser or getattr(current_user, 'user_type', None) == "admin"):
            logging.warning(f"User {current_user_id} attempted to access events for user {user_id}")
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        # Get current date for filtering
        current_date = datetime.now()
        
        # Get user registrations with event details
        try:
            # Build the base query
            query = db.query(models.Registration, models.Event)\
                .join(models.Event, models.Registration.event_id == models.Event.id)\
                .filter(models.Registration.user_id == user_id)
            
            # Apply status filter if provided
            if status:
                if status.lower() == "upcoming":
                    query = query.filter(models.Event.start_time > current_date)
                elif status.lower() == "past":
                    query = query.filter(models.Event.start_time <= current_date)
            
            # Get results
            results = query.order_by(models.Event.start_time.asc()).limit(limit).all()
            
            # Format the response
            user_events = []
            for registration, event in results:
                event_data = {
                    "id": event.id,
                    "title": event.title,
                    "description": event.description,
                    "event_type": event.event_type,
                    "location": event.location,
                    "start_time": event.start_time.isoformat() if event.start_time else None,
                    "end_time": event.end_time.isoformat() if event.end_time else None,
                    "is_active": event.is_active,
                    "image_url": event.image_url if hasattr(event, 'image_url') else None,
                    "price": float(event.price) if event.price is not None else 0.0,
                    "registration_status": registration.status,
                    "registration_date": registration.registration_date.isoformat() if registration.registration_date else None,
                    "payment_status": registration.payment_status if hasattr(registration, 'payment_status') else None
                }
                user_events.append(event_data)
            
            logging.info(f"Retrieved {len(user_events)} events for user {user_id}")
            return user_events
            
        except SQLAlchemyError as db_error:
            logging.error(f"Database error in get_user_events: {str(db_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred when retrieving user events"
            )
            
    except Exception as e:
        logging.error(f"Unexpected error in get_user_events: {str(e)}", exc_info=True)
        # Return empty list as fallback
        return []


@router.get("/{user_id}/points/history", response_model=List[Dict])
@safe_api_call
def get_user_points_history(
    request: Request,
    user_id: int,
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 30,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get points history for a specific user.
    
    Returns a list of point transactions with details about each transaction.
    Regular users can only view their own history, while admins can view any user's history.
    """
    try:
        # Check permissions - users can only view their own history unless they're admins
        current_user_id = safe_get_user_id(current_user)
        if current_user_id is None:
            logging.warning(f"User ID is None when fetching points history for user {user_id}")
            raise HTTPException(status_code=401, detail="Authentication required")
            
        if current_user_id != user_id and not (current_user.is_superuser or current_user.user_type == "admin"):
            logging.warning(f"User {current_user_id} attempted to access points history for user {user_id}")
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        try:
            # Get transactions from database
            transactions = db.query(models.PointsTransaction).filter(
                models.PointsTransaction.user_id == user_id
            ).order_by(models.PointsTransaction.transaction_date.desc()).offset(skip).limit(limit).all()
            
            # Format the transactions for response
            history = []
            for tx in transactions:
                # Get associated event information if available
                event_info = None
                if tx.event_id:
                    try:
                        event = db.query(models.Event).filter(models.Event.id == tx.event_id).first()
                        if event:
                            event_info = {
                                "id": event.id,
                                "title": event.title,
                                "event_type": event.event_type,
                                "start_time": event.start_time.isoformat() if event.start_time else None
                            }
                    except Exception as event_error:
                        logging.error(f"Error getting event info for transaction {tx.id}: {str(event_error)}")
                
                # Format transaction for response
                history_item = {
                    "id": tx.id,
                    "points": tx.points,
                    "transaction_type": tx.transaction_type,
                    "description": tx.description,
                    "transaction_date": tx.transaction_date.isoformat() if tx.transaction_date else None,
                    "event": event_info
                }
                history.append(history_item)
            
            logging.info(f"Retrieved {len(history)} points history items for user {user_id}")
            return history
            
        except SQLAlchemyError as db_error:
            logging.error(f"Database error in get_user_points_history: {str(db_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred when retrieving points history"
            )
            
    except Exception as e:
        logging.error(f"Unexpected error in get_user_points_history: {str(e)}", exc_info=True)
        # Return empty list as fallback
        return []