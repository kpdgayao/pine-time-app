from typing import Any, List, Dict, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

from app import models, schemas
from app.api import dependencies
from app.services.points_manager import PointsManager
from app.api.dependencies import safe_api_call, safe_api_response_handler, safe_get_user_id

router = APIRouter()


@router.get("/", response_model=List[Dict])
@safe_api_call
def read_badges(
    request: Request,
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Retrieve all available badge types with their criteria.
    
    Returns a list of all badge types, their descriptions, and the criteria required to earn them.
    This endpoint is available to all authenticated users.
    """
    # Define all available badge types with their criteria
    available_badges = [
        # Event Master badges
        {
            "badge_type": "event_master_bronze",
            "name": "Event Master Bronze",
            "description": "Attended 5 or more events",
            "criteria_type": "attendance",
            "criteria_threshold": 5,
            "level": "bronze",
            "image_url": "/static/badges/event_master_bronze.png"
        },
        {
            "badge_type": "event_master_silver",
            "name": "Event Master Silver",
            "description": "Attended 15 or more events",
            "criteria_type": "attendance",
            "criteria_threshold": 15,
            "level": "silver",
            "image_url": "/static/badges/event_master_silver.png"
        },
        {
            "badge_type": "event_master_gold",
            "name": "Event Master Gold",
            "description": "Attended 30 or more events",
            "criteria_type": "attendance",
            "criteria_threshold": 30,
            "level": "gold",
            "image_url": "/static/badges/event_master_gold.png"
        },
        
        # Points Collector badges
        {
            "badge_type": "points_collector_bronze",
            "name": "Points Collector Bronze",
            "description": "Earned 500 or more points",
            "criteria_type": "points",
            "criteria_threshold": 500,
            "level": "bronze",
            "image_url": "/static/badges/points_collector_bronze.png"
        },
        {
            "badge_type": "points_collector_silver",
            "name": "Points Collector Silver",
            "description": "Earned 2000 or more points",
            "criteria_type": "points",
            "criteria_threshold": 2000,
            "level": "silver",
            "image_url": "/static/badges/points_collector_silver.png"
        },
        {
            "badge_type": "points_collector_gold",
            "name": "Points Collector Gold",
            "description": "Earned 5000 or more points",
            "criteria_type": "points",
            "criteria_threshold": 5000,
            "level": "gold",
            "image_url": "/static/badges/points_collector_gold.png"
        },
        
        # Streak Master badges
        {
            "badge_type": "streak_master_bronze",
            "name": "Streak Master Bronze",
            "description": "Attended events for 3 consecutive weeks",
            "criteria_type": "streak",
            "criteria_threshold": 3,
            "level": "bronze",
            "image_url": "/static/badges/streak_master_bronze.png"
        },
        {
            "badge_type": "streak_master_silver",
            "name": "Streak Master Silver",
            "description": "Attended events for 8 consecutive weeks",
            "criteria_type": "streak",
            "criteria_threshold": 8,
            "level": "silver",
            "image_url": "/static/badges/streak_master_silver.png"
        },
        {
            "badge_type": "streak_master_gold",
            "name": "Streak Master Gold",
            "description": "Attended events for 12 consecutive weeks",
            "criteria_type": "streak",
            "criteria_threshold": 12,
            "level": "gold",
            "image_url": "/static/badges/streak_master_gold.png"
        },
        
        # Trivia Champion badges
        {
            "badge_type": "trivia_champion_bronze",
            "name": "Trivia Champion Bronze",
            "description": "Attended 3 or more trivia events",
            "criteria_type": "event_type",
            "event_type": "trivia",
            "criteria_threshold": 3,
            "level": "bronze",
            "image_url": "/static/badges/trivia_champion_bronze.png"
        },
        {
            "badge_type": "trivia_champion_silver",
            "name": "Trivia Champion Silver",
            "description": "Attended 8 or more trivia events",
            "criteria_type": "event_type",
            "event_type": "trivia",
            "criteria_threshold": 8,
            "level": "silver",
            "image_url": "/static/badges/trivia_champion_silver.png"
        },
        {
            "badge_type": "trivia_champion_gold",
            "name": "Trivia Champion Gold",
            "description": "Attended 15 or more trivia events",
            "criteria_type": "event_type",
            "event_type": "trivia",
            "criteria_threshold": 15,
            "level": "gold",
            "image_url": "/static/badges/trivia_champion_gold.png"
        },
        
        # Game Night Enthusiast badges
        {
            "badge_type": "game_night_enthusiast_bronze",
            "name": "Game Night Enthusiast Bronze",
            "description": "Attended 3 or more game night events",
            "criteria_type": "event_type",
            "event_type": "game_night",
            "criteria_threshold": 3,
            "level": "bronze",
            "image_url": "/static/badges/game_night_enthusiast_bronze.png"
        },
        {
            "badge_type": "game_night_enthusiast_silver",
            "name": "Game Night Enthusiast Silver",
            "description": "Attended 8 or more game night events",
            "criteria_type": "event_type",
            "event_type": "game_night",
            "criteria_threshold": 8,
            "level": "silver",
            "image_url": "/static/badges/game_night_enthusiast_silver.png"
        },
        {
            "badge_type": "game_night_enthusiast_gold",
            "name": "Game Night Enthusiast Gold",
            "description": "Attended 15 or more game night events",
            "criteria_type": "event_type",
            "event_type": "game_night",
            "criteria_threshold": 15,
            "level": "gold",
            "image_url": "/static/badges/game_night_enthusiast_gold.png"
        },
    ]
    
    try:
        # Get user's earned badges to mark which ones they have
        points_manager = PointsManager(db)
        user_id = safe_get_user_id(current_user)
        
        if user_id is None:
            logging.warning("User ID is None when fetching badges")
            # Return badges without earned status if user ID is not available
            return safe_api_response_handler(available_badges[skip:skip+limit])
        
        user_badges = points_manager.get_user_badges(user_id)
        user_badge_types = [badge.badge_type for badge in user_badges] if user_badges else []
        
        # Mark which badges the user has earned
        for badge in available_badges:
            badge["earned"] = badge["badge_type"] in user_badge_types
        
        # Apply pagination
        result = available_badges[skip:skip+limit]
        logging.info(f"Retrieved {len(result)} badges for user {user_id}")
        return safe_api_response_handler(result)
        
    except SQLAlchemyError as e:
        logging.error(f"Database error in read_badges: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred when retrieving badges"
        )
        
    except Exception as e:
        logging.error(f"Unexpected error in read_badges: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred when retrieving badges"
        )


@router.get("/me", response_model=List[schemas.BadgeOut])
@safe_api_call
def read_user_badges(
    request: Request,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get current user's earned badges.
    
    Returns all badges that the current user has earned, organized by category and level.
    """
    try:
        points_manager = PointsManager(db)
        user_id = safe_get_user_id(current_user)
        
        if user_id is None:
            logging.warning("User ID is None when fetching user badges")
            return []
        
        user_badges = points_manager.get_user_badges(user_id)
        logging.info(f"Retrieved {len(user_badges) if user_badges else 0} badges for user {user_id}")
        
        # Return empty list instead of None to prevent NoneType errors
        return user_badges if user_badges else []
        
    except SQLAlchemyError as e:
        logging.error(f"Database error in read_user_badges: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred when retrieving user badges"
        )
        
    except Exception as e:
        logging.error(f"Unexpected error in read_user_badges: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred when retrieving user badges"
        )

@router.get("/users/{user_id}", response_model=List[schemas.BadgeOut])
@safe_api_call
def read_badges_for_user(
    user_id: int,
    request: Request,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get all badges for a specific user (admin only).
    """
    try:
        if not (current_user.is_superuser or getattr(current_user, 'user_type', None) == "admin"):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        # Validate user exists
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        points_manager = PointsManager(db)
        user_badges = points_manager.get_user_badges(user_id)
        logging.info(f"Admin {current_user.id} retrieved {len(user_badges) if user_badges else 0} badges for user {user_id}")
        
        # Return empty list instead of None to prevent NoneType errors
        return user_badges if user_badges else []
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
        
    except SQLAlchemyError as e:
        logging.error(f"Database error in read_badges_for_user: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred when retrieving user badges"
        )
        
    except Exception as e:
        logging.error(f"Unexpected error in read_badges_for_user: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred when retrieving user badges"
        )


@router.get("/users/me/badges", response_model=Dict)
@safe_api_call
def read_user_badges_detailed(
    request: Request,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get current user's earned badges with detailed information.
    
    Returns all badges that the current user has earned, organized by category and level,
    along with progress information towards the next level badges.
    """
    try:
        user_id = safe_get_user_id(current_user)
        if user_id is None:
            logging.warning("User ID is None when fetching detailed user badges")
            return {"categories": {}, "progress": {}}
            
        points_manager = PointsManager(db)
        badges = []
        attended_events = 0
        points_balance = 0
        streak_weeks = 0
        event_type_counts = {}
        
        try:
            # Get user's badges with user_badge relationship
            user_badges = db.query(models.UserBadge).filter(
                models.UserBadge.user_id == user_id
            ).all()
            
            # Get user's progress information
            attended_events = db.query(models.Registration).filter(
                models.Registration.user_id == user_id,
                models.Registration.status == "attended"
            ).count()
            
            points_balance = points_manager.get_user_points_balance(user_id)
            streak_weeks = points_manager.calculate_attendance_streak(user_id)
            
            # Get event type counts
            event_type_counts = {}
            attended_registrations = db.query(models.Registration).filter(
                models.Registration.user_id == user_id,
                models.Registration.status == "attended"
            ).all()
            
            for registration in attended_registrations:
                try:
                    event = db.query(models.Event).filter(models.Event.id == registration.event_id).first()
                    if event:
                        event_type_counts[event.event_type] = event_type_counts.get(event.event_type, 0) + 1
                except Exception as event_error:
                    logging.error(f"Error getting event type for registration {registration.id}: {str(event_error)}")
                    continue
        except SQLAlchemyError as db_error:
            logging.error(f"Database error in read_user_badges_detailed: {str(db_error)}")
            # Continue with empty data
            user_badges = []
            attended_events = 0
            points_balance = 0
            streak_weeks = 0
            event_type_counts = {}
    
        # Organize badges by category
        badge_categories = {
            "event_master": {
                "name": "Event Master",
                "description": "Awarded for attending events",
                "progress": attended_events,
                "next_threshold": 30 if attended_events < 30 else (15 if attended_events < 15 else 5),
                "badges": []
            },
            "points_collector": {
                "name": "Points Collector",
                "description": "Awarded for earning points",
                "progress": points_balance,
                "next_threshold": 5000 if points_balance < 5000 else (2000 if points_balance < 2000 else 500),
                "badges": []
            },
            "streak_master": {
                "name": "Streak Master",
                "description": "Awarded for consecutive weekly attendance",
                "progress": streak_weeks,
                "next_threshold": 12 if streak_weeks < 12 else (8 if streak_weeks < 8 else 3),
                "badges": []
            },
            "trivia_champion": {
                "name": "Trivia Champion",
                "description": "Awarded for attending trivia events",
                "progress": event_type_counts.get("trivia", 0),
                "next_threshold": 15 if event_type_counts.get("trivia", 0) < 15 else (8 if event_type_counts.get("trivia", 0) < 8 else 3),
                "badges": []
            },
            "game_night_enthusiast": {
                "name": "Game Night Enthusiast",
                "description": "Awarded for attending game night events",
                "progress": event_type_counts.get("game_night", 0),
                "next_threshold": 15 if event_type_counts.get("game_night", 0) < 15 else (8 if event_type_counts.get("game_night", 0) < 8 else 3),
                "badges": []
            }
        }
        
        # Process user badges
        for user_badge in user_badges:
            try:
                badge = user_badge.badge
                if not badge:
                    continue
                    
                # Determine category based on badge type
                category = None
                if hasattr(badge, 'category') and badge.category in badge_categories:
                    category = badge.category
                elif hasattr(badge, 'badge_type_obj'):
                    badge_type = badge.badge_type_obj.badge_type if badge.badge_type_obj else None
                    
                    if "event_master" in badge_type:
                        category = "event_master"
                    elif "points_collector" in badge_type:
                        category = "points_collector"
                    elif "streak_master" in badge_type:
                        category = "streak_master"
                    elif "trivia_champion" in badge_type:
                        category = "trivia_champion"
                    elif "game_night_enthusiast" in badge_type:
                        category = "game_night_enthusiast"
                
                if category and category in badge_categories:
                    badge_info = {
                        "id": badge.id,
                        "name": badge.name,
                        "description": badge.description,
                        "image_url": badge.icon_url if hasattr(badge, 'icon_url') else None,
                        "earned_date": user_badge.earned_date.isoformat() if hasattr(user_badge, 'earned_date') else None,
                        "level": user_badge.level if hasattr(user_badge, 'level') else 1
                    }
                    badge_categories[category]["badges"].append(badge_info)
            except Exception as badge_error:
                logging.error(f"Error processing badge {user_badge.badge_id if hasattr(user_badge, 'badge_id') else 'unknown'}: {str(badge_error)}")
                continue
        
        # Calculate progress percentages
        progress = {
            "events": {
                "current": attended_events,
                "next_threshold": 5 if attended_events < 5 else 15 if attended_events < 15 else 30,
                "percentage": min(100, (attended_events / (5 if attended_events < 5 else 15 if attended_events < 15 else 30)) * 100)
            },
            "points": {
                "current": points_balance,
                "next_threshold": 500 if points_balance < 500 else 2000 if points_balance < 2000 else 5000,
                "percentage": min(100, (points_balance / (500 if points_balance < 500 else 2000 if points_balance < 2000 else 5000)) * 100)
            },
            "streak": {
                "current": streak_weeks,
                "next_threshold": 3 if streak_weeks < 3 else 8 if streak_weeks < 8 else 12,
                "percentage": min(100, (streak_weeks / (3 if streak_weeks < 3 else 8 if streak_weeks < 8 else 12)) * 100)
            }
        }
        
        # Add event type progress
        for event_type, count in event_type_counts.items():
            progress[f"event_type_{event_type}"] = {
                "current": count,
                "next_threshold": 3 if count < 3 else 8 if count < 8 else 15,
                "percentage": min(100, (count / (3 if count < 3 else 8 if count < 8 else 15)) * 100)
            }
        
        logging.info(f"Retrieved detailed badge information for user {user_id}")
        return {
            "categories": badge_categories,
            "progress": progress
        }
        
    except Exception as e:
        logging.error(f"Unexpected error in read_user_badges_detailed: {str(e)}", exc_info=True)
        # Return empty data as fallback
        return {
            "categories": {},
            "progress": {}
        }


@router.get("/{badge_id}", response_model=schemas.BadgeOut)
@safe_api_call
def read_badge(
    *,
    request: Request,
    db: Session = Depends(dependencies.get_db),
    badge_id: int,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get badge by ID.
    
    Retrieves detailed information about a specific badge by its ID.
    Users can only view their own badges unless they have admin privileges.
    """
    try:
        user_id = safe_get_user_id(current_user)
        if user_id is None:
            logging.warning(f"User ID is None when fetching badge {badge_id}")
            raise HTTPException(status_code=401, detail="Authentication required")
            
        try:
            badge = db.query(models.Badge).filter(models.Badge.id == badge_id).first()
            if not badge:
                logging.warning(f"Badge with ID {badge_id} not found")
                raise HTTPException(status_code=404, detail="Badge not found")
            
            # Check if user has permission to see this badge
            if not (current_user.is_superuser or current_user.user_type == "admin" or 
                   (hasattr(badge, 'user_id') and badge.user_id == user_id)):
                logging.warning(f"User {user_id} attempted to access badge {badge_id} without permission")
                raise HTTPException(status_code=403, detail="Not enough permissions")
                
            logging.info(f"Retrieved badge {badge_id} for user {user_id}")
            return badge
            
        except SQLAlchemyError as db_error:
            logging.error(f"Database error in read_badge: {str(db_error)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Database error occurred when retrieving badge"
            )
            
    except Exception as e:
        logging.error(f"Unexpected error in read_badge: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred when retrieving badge"
        )
    
    return badge
