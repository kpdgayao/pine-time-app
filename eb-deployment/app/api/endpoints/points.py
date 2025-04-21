from typing import Any, List

from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session

from app import models, schemas
from app.api import dependencies
from app.services.points_manager import PointsManager

router = APIRouter()


@router.get("/balance", response_model=int)
def get_points_balance(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get current user's points balance.
    """
    points_manager = PointsManager(db)
    balance = points_manager.get_user_points_balance(current_user.id)
    return balance


@router.get("/transactions", response_model=List[schemas.PointsTransaction])
def get_user_transactions(
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get current user's points transactions.
    """
    transactions = db.query(models.PointsTransaction).filter(
        models.PointsTransaction.user_id == current_user.id
    ).order_by(models.PointsTransaction.transaction_date.desc()).offset(skip).limit(limit).all()
    
    return transactions


@router.post("/award", response_model=schemas.PointsTransaction)
def award_points(
    *,
    db: Session = Depends(dependencies.get_db),
    user_id: int = Body(...),
    points: int = Body(..., gt=0),
    description: str = Body(...),
    event_id: int = Body(None),
    current_user: models.User = Depends(dependencies.get_current_active_superuser),
) -> Any:
    """
    Award points to a user (admin only).
    """
    points_manager = PointsManager(db)
    
    try:
        transaction = points_manager.award_points(
            user_id=user_id,
            points=points,
            transaction_type="earned",
            description=description,
            event_id=event_id
        )
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/redeem", response_model=schemas.PointsTransaction)
def redeem_points(
    *,
    db: Session = Depends(dependencies.get_db),
    points: int = Body(..., gt=0),
    description: str = Body(...),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Redeem points for the current user.
    """
    points_manager = PointsManager(db)
    
    # Check if user has enough points
    balance = points_manager.get_user_points_balance(current_user.id)
    if balance < points:
        raise HTTPException(status_code=400, detail="Not enough points")
    
    try:
        transaction = points_manager.award_points(
            user_id=current_user.id,
            points=-points,  # Negative points for redemption
            transaction_type="redeemed",
            description=description
        )
        return transaction
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/leaderboard", response_model=List[dict])
def get_points_leaderboard(
    db: Session = Depends(dependencies.get_db),
    limit: int = 10,
    time_period: str = "all_time",  # Options: all_time, weekly, monthly
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get points leaderboard.
    
    Returns a leaderboard of users ranked by their points.
    Can filter by time period: all_time, weekly, or monthly.
    """
    from datetime import datetime, timedelta
    from sqlalchemy import func, desc
    
    now = datetime.utcnow()
    
    # Define time period filter
    if time_period == "weekly":
        # Start of current week (Monday)
        start_date = now - timedelta(days=now.weekday(), hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
    elif time_period == "monthly":
        # Start of current month
        start_date = datetime(now.year, now.month, 1)
    else:  # all_time or invalid value
        start_date = None
    
    # Get users with their points
    if start_date:
        # For weekly or monthly leaderboard, use transactions within the time period
        leaderboard_query = db.query(
            models.PointsTransaction.user_id,
            func.sum(models.PointsTransaction.points).label("total_points")
        ).filter(
            models.PointsTransaction.transaction_date >= start_date
        ).group_by(
            models.PointsTransaction.user_id
        ).order_by(
            desc("total_points")
        ).limit(limit).all()
        
        # Get user details for each entry
        leaderboard = []
        for user_id, points in leaderboard_query:
            user = db.query(models.User).filter(models.User.id == user_id).first()
            if user:
                leaderboard.append({
                    "user_id": user.id,
                    "username": user.username,
                    "full_name": getattr(user, "full_name", None),
                    "points": points,
                    "rank": len(leaderboard) + 1,
                    "is_current_user": user.id == current_user.id
                })
    else:
        # For all-time leaderboard, use the points manager to get accurate balances
        points_manager = PointsManager(db)
        users = db.query(models.User).filter(models.User.is_active == True).all()
        
        leaderboard = []
        for user in users:
            points = points_manager.get_user_points_balance(user.id)
            if points > 0:  # Only include users with points
                leaderboard.append({
                    "user_id": user.id,
                    "username": user.username,
                    "full_name": getattr(user, "full_name", None),
                    "points": points,
                    "is_current_user": user.id == current_user.id
                })
        
        # Sort by points (descending)
        leaderboard.sort(key=lambda x: x["points"], reverse=True)
        
        # Add rank
        for i, entry in enumerate(leaderboard):
            entry["rank"] = i + 1
        
        # Limit results
        leaderboard = leaderboard[:limit]
    
    # Find current user's rank if not in the top results
    current_user_in_results = any(entry["user_id"] == current_user.id for entry in leaderboard)
    
    if not current_user_in_results:
        # Get current user's points
        if start_date:
            current_user_points = db.query(
                func.sum(models.PointsTransaction.points)
            ).filter(
                models.PointsTransaction.user_id == current_user.id,
                models.PointsTransaction.transaction_date >= start_date
            ).scalar() or 0
        else:
            points_manager = PointsManager(db)
            current_user_points = points_manager.get_user_points_balance(current_user.id)
        
        # Get number of users with more points
        if start_date:
            higher_ranks = db.query(
                models.PointsTransaction.user_id
            ).filter(
                models.PointsTransaction.transaction_date >= start_date
            ).group_by(
                models.PointsTransaction.user_id
            ).having(
                func.sum(models.PointsTransaction.points) > current_user_points
            ).count()
        else:
            # For all-time, this is more complex
            # We'll approximate by checking if any user has more points
            higher_ranks = 0
            for user in users:
                if user.id != current_user.id:
                    user_points = points_manager.get_user_points_balance(user.id)
                    if user_points > current_user_points:
                        higher_ranks += 1
        
        # Add current user to the results with their rank
        if current_user_points > 0:
            current_user_entry = {
                "user_id": current_user.id,
                "username": current_user.username,
                "full_name": getattr(current_user, "full_name", None),
                "points": current_user_points,
                "rank": higher_ranks + 1,
                "is_current_user": True
            }
            leaderboard.append(current_user_entry)
    
    return leaderboard


@router.get("/stats", response_model=dict)
def get_user_points_stats(
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get detailed statistics about a user's points.
    
    Returns information about points earned, redeemed, and a breakdown by categories.
    """
    from sqlalchemy import func
    from datetime import datetime, timedelta
    
    points_manager = PointsManager(db)
    now = datetime.utcnow()
    
    # Get current balance
    current_balance = points_manager.get_user_points_balance(current_user.id)
    
    # Get total earned and redeemed
    total_earned = db.query(func.sum(models.PointsTransaction.points)).filter(
        models.PointsTransaction.user_id == current_user.id,
        models.PointsTransaction.transaction_type == "earned"
    ).scalar() or 0
    
    total_redeemed = db.query(func.sum(models.PointsTransaction.points)).filter(
        models.PointsTransaction.user_id == current_user.id,
        models.PointsTransaction.transaction_type == "redeemed"
    ).scalar() or 0
    
    # Get points earned this week
    week_start = now - timedelta(days=now.weekday(), hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
    earned_this_week = db.query(func.sum(models.PointsTransaction.points)).filter(
        models.PointsTransaction.user_id == current_user.id,
        models.PointsTransaction.transaction_type == "earned",
        models.PointsTransaction.transaction_date >= week_start
    ).scalar() or 0
    
    # Get points earned this month
    month_start = datetime(now.year, now.month, 1)
    earned_this_month = db.query(func.sum(models.PointsTransaction.points)).filter(
        models.PointsTransaction.user_id == current_user.id,
        models.PointsTransaction.transaction_type == "earned",
        models.PointsTransaction.transaction_date >= month_start
    ).scalar() or 0
    
    # Get breakdown by event type
    event_type_breakdown = []
    event_points = db.query(
        models.Event.event_type,
        func.sum(models.PointsTransaction.points).label("points")
    ).join(
        models.PointsTransaction,
        models.PointsTransaction.event_id == models.Event.id
    ).filter(
        models.PointsTransaction.user_id == current_user.id,
        models.PointsTransaction.transaction_type == "earned"
    ).group_by(
        models.Event.event_type
    ).all()
    
    for event_type, points in event_points:
        event_type_breakdown.append({
            "event_type": event_type,
            "points": points
        })
    
    # Get recent transactions
    recent_transactions = db.query(models.PointsTransaction).filter(
        models.PointsTransaction.user_id == current_user.id
    ).order_by(
        models.PointsTransaction.transaction_date.desc()
    ).limit(5).all()
    
    recent_transactions_data = []
    for transaction in recent_transactions:
        recent_transactions_data.append({
            "id": transaction.id,
            "points": transaction.points,
            "transaction_type": transaction.transaction_type,
            "description": transaction.description,
            "transaction_date": transaction.transaction_date
        })
    
    # Get user rank
    leaderboard = get_points_leaderboard(db=db, limit=1000, current_user=current_user)
    user_rank = next((entry["rank"] for entry in leaderboard if entry["user_id"] == current_user.id), None)
    
    return {
        "current_balance": current_balance,
        "total_earned": total_earned,
        "total_redeemed": abs(total_redeemed),
        "earned_this_week": earned_this_week,
        "earned_this_month": earned_this_month,
        "user_rank": user_rank,
        "event_type_breakdown": event_type_breakdown,
        "recent_transactions": recent_transactions_data
    }
