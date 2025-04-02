from typing import Any, List, Dict

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import dependencies
from app.services.points_manager import PointsManager

router = APIRouter()


@router.get("/", response_model=List[Dict])
def read_badges(
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
    
    # Get user's earned badges to mark which ones they have
    points_manager = PointsManager(db)
    user_badges = points_manager.get_user_badges(current_user.id)
    user_badge_types = [badge.badge_type for badge in user_badges]
    
    # Mark which badges the user has earned
    for badge in available_badges:
        badge["earned"] = badge["badge_type"] in user_badge_types
    
    # Apply pagination
    return available_badges[skip:skip+limit]


@router.get("/me", response_model=List[schemas.Badge])
def read_user_badges(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get current user's earned badges.
    
    Returns all badges that the current user has earned, organized by category and level.
    """
    badges = db.query(models.Badge).filter(
        models.Badge.user_id == current_user.id
    ).all()
    
    return badges


@router.get("/users/me/badges", response_model=Dict)
def read_user_badges_detailed(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get current user's earned badges with detailed information.
    
    Returns all badges that the current user has earned, organized by category and level,
    along with progress information towards the next level badges.
    """
    points_manager = PointsManager(db)
    
    # Get user's badges
    badges = db.query(models.Badge).filter(
        models.Badge.user_id == current_user.id
    ).all()
    
    # Get user's progress information
    attended_events = db.query(models.Registration).filter(
        models.Registration.user_id == current_user.id,
        models.Registration.status == "attended"
    ).count()
    
    points_balance = points_manager.get_user_points_balance(current_user.id)
    streak_weeks = points_manager.calculate_attendance_streak(current_user.id)
    
    # Get event type counts
    event_type_counts = {}
    attended_registrations = db.query(models.Registration).filter(
        models.Registration.user_id == current_user.id,
        models.Registration.status == "attended"
    ).all()
    
    for registration in attended_registrations:
        event = db.query(models.Event).filter(models.Event.id == registration.event_id).first()
        if event:
            event_type_counts[event.event_type] = event_type_counts.get(event.event_type, 0) + 1
    
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
    
    # Organize badges by category
    for badge in badges:
        badge_type_parts = badge.badge_type.split("_")
        level = badge_type_parts[-1] if badge_type_parts[-1] in ["bronze", "silver", "gold"] else None
        
        # Determine category
        category = None
        if "event_master" in badge.badge_type:
            category = "event_master"
        elif "points_collector" in badge.badge_type:
            category = "points_collector"
        elif "streak_master" in badge.badge_type:
            category = "streak_master"
        elif "trivia_champion" in badge.badge_type:
            category = "trivia_champion"
        elif "game_night_enthusiast" in badge.badge_type:
            category = "game_night_enthusiast"
        
        if category:
            badge_info = {
                "id": badge.id,
                "name": badge.name,
                "description": badge.description,
                "image_url": badge.image_url,
                "earned_date": badge.earned_date,
                "level": level
            }
            badge_categories[category]["badges"].append(badge_info)
    
    return badge_categories


@router.get("/{badge_id}", response_model=schemas.Badge)
def read_badge(
    *,
    db: Session = Depends(dependencies.get_db),
    badge_id: int,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get badge by ID.
    
    Retrieves detailed information about a specific badge by its ID.
    Users can only view their own badges unless they have admin privileges.
    """
    badge = db.query(models.Badge).filter(models.Badge.id == badge_id).first()
    if not badge:
        raise HTTPException(status_code=404, detail="Badge not found")
    
    # Check if user has permission to see this badge
    if not (current_user.is_superuser or current_user.user_type == "admin" or badge.user_id == current_user.id):
        raise HTTPException(status_code=403, detail="Not enough permissions")
    
    return badge
