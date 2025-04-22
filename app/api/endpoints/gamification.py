from typing import Any, List, Dict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
import logging

from app import models, schemas
from app.api import dependencies
from app.services.points_manager import PointsManager
from app.services.badge_manager import BadgeManager

router = APIRouter()


@router.get("/users/{user_id}/points", response_model=schemas.UserPoints)
def get_user_points(
    user_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get user points balance.
    """
    try:
        # Check if user exists
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check permissions - users can only see their own points unless they're admin
        if current_user.id != user_id and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        # Get points balance
        points_manager = PointsManager(db)
        balance = points_manager.get_user_points_balance(user_id)
        
        return {"points": balance, "user_id": user_id}
    except Exception as e:
        # Log the error
        logging.error(f"Error in get_user_points: {str(e)}")
        # Return a graceful error response
        raise HTTPException(status_code=500, detail="An error occurred while fetching user points")


@router.get("/users/{user_id}/badges", response_model=List[Dict[str, Any]])
def get_user_badges(
    user_id: int,
    include_progress: bool = False,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get user badges with optional progress information.
    """
    try:
        # Check if user exists
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check permissions - users can only see their own badges unless they're admin
        if current_user.id != user_id and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        # Get user badges
        badge_manager = BadgeManager(db)
        user_badges = badge_manager.get_user_badges(user_id)
        
        # Add progress information if requested
        if include_progress:
            for badge in user_badges:
                # Add progress information
                badge["progress"] = badge_manager.get_badge_progress(user_id, badge["badge_id"])
                badge["next_level_threshold"] = badge_manager.get_next_level_threshold(badge["badge_id"], badge["level"])
                # Mark new badges (earned in the last 7 days)
                if badge["earned_date"] and (datetime.utcnow() - badge["earned_date"]).days <= 7:
                    badge["is_new"] = True
                else:
                    badge["is_new"] = False
        
        return user_badges
    except Exception as e:
        # Log the error
        logging.error(f"Error in get_user_badges: {str(e)}")
        # Return a graceful error response
        raise HTTPException(status_code=500, detail="An error occurred while fetching user badges")


@router.get("/users/{user_id}/stats", response_model=schemas.UserStats)
def get_user_stats(
    user_id: int,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get comprehensive user statistics including points, badges, streak, and engagement metrics.
    """
    try:
        # Check if user exists
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check permissions - users can only see their own stats unless they're admin
        if current_user.id != user_id and not current_user.is_superuser:
            raise HTTPException(status_code=403, detail="Not enough permissions")
        
        # Get points balance
        points_manager = PointsManager(db)
        balance = points_manager.get_user_points_balance(user_id)
        
        # Get badges count
        badge_manager = BadgeManager(db)
        badges = badge_manager.get_user_badges(user_id)
        badges_count = len(badges)
        
        # Get user's rank in leaderboard
        rank = points_manager.get_user_rank(user_id)
        total_users = db.query(models.User).filter(models.User.is_active == True).count()
        
        # Get streak information
        streak_count = points_manager.get_user_streak(user_id)
        
        # Get events attended count with safe handling for EventAttendee model
        try:
            # First try using Registration model which is more likely to exist
            try:
                events_attended = db.query(models.Registration).filter(
                    models.Registration.user_id == user_id,
                    models.Registration.status == "attended"
                ).count()
                logging.info(f"Found {events_attended} attended events for user {user_id} using Registration model")
            except Exception as reg_error:
                logging.warning(f"Error using Registration model: {str(reg_error)}")
                
                # Fall back to EventAttendee if it exists
                if hasattr(models, 'EventAttendee'):
                    events_attended = db.query(models.EventAttendee).filter(
                        models.EventAttendee.user_id == user_id,
                        models.EventAttendee.status == "attended"
                    ).count()
                    logging.info(f"Found {events_attended} attended events for user {user_id} using EventAttendee model")
                else:
                    logging.warning("EventAttendee model not found, using default value for events_attended")
                    events_attended = 0
        except Exception as e:
            logging.error(f"Error getting events attended: {str(e)}")
            events_attended = 0
        
        # Get recent activities
        recent_transactions = db.query(models.PointsTransaction).filter(
            models.PointsTransaction.user_id == user_id
        ).order_by(models.PointsTransaction.transaction_date.desc()).limit(5).all()
        
        recent_activities = [
            {
                "id": tx.id,
                "type": "points",
                "description": tx.description,
                "points": tx.points,
                "date": tx.transaction_date,
                "event_id": tx.event_id
            } for tx in recent_transactions
        ]
        
        # Compile stats
        stats = {
            "total_points": balance,
            "total_badges": badges_count,
            "rank": rank,
            "total_users": total_users,
            "streak_count": streak_count,
            "events_attended": events_attended,
            "recent_activities": recent_activities
        }
        
        return stats
    except Exception as e:
        # Log the error
        logging.error(f"Error in get_user_stats: {str(e)}")
        # Return a graceful error response with fallback data
        return {
            "total_points": 0,
            "total_badges": 0,
            "rank": 0,
            "total_users": 0,
            "streak_count": 0,
            "events_attended": 0,
            "recent_activities": []
        }
