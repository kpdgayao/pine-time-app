from typing import Any, List, Dict, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Body, Request, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.sql import func
import logging

from app import models, schemas
from app.api import dependencies
from app.services.points_manager import PointsManager
from app.api.dependencies import safe_api_call, safe_api_response_handler, safe_get_user_id, safe_sqlalchemy_to_pydantic

router = APIRouter()


@router.get("/activities", response_model=List[Dict])
@safe_api_call
def get_user_activities(
    request: Request,
    db: Session = Depends(dependencies.get_db),
    time_period: str = "all_time",  # Options: all_time, weekly, monthly
    sort: str = "desc",  # Options: asc, desc
    limit: int = 20,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get current user's recent activities with filtering options.
    
    Parameters:
    - time_period: Filter by time period (all_time, weekly, monthly)
    - sort: Sort order (asc, desc)
    - limit: Maximum number of items to return
    
    Returns a list of recent activities including points transactions and event attendance.
    """
    try:
        user_id = safe_get_user_id(current_user)
        if user_id is None:
            logging.warning("User ID is None when fetching activities")
            return []
        
        # Get current date for filtering
        from datetime import datetime, timedelta
        current_date = datetime.now()
        
        # Set date filter based on time_period
        date_filter = None
        if time_period == "weekly":
            date_filter = current_date - timedelta(days=7)
        elif time_period == "monthly":
            date_filter = current_date - timedelta(days=30)
        
        # Get points transactions
        transactions_query = db.query(models.PointsTransaction).filter(
            models.PointsTransaction.user_id == user_id
        )
        
        # Apply date filter if specified
        if date_filter:
            transactions_query = transactions_query.filter(
                models.PointsTransaction.timestamp >= date_filter
            )
        
        # Apply sort order
        if sort.lower() == "asc":
            transactions_query = transactions_query.order_by(models.PointsTransaction.timestamp.asc())
        else:
            transactions_query = transactions_query.order_by(models.PointsTransaction.timestamp.desc())
        
        # Get transactions
        transactions = transactions_query.limit(limit).all()
        
        # Format activities
        activities = []
        for tx in transactions:
            activity_type = "points_earned" if tx.points > 0 else "points_spent"
            
            # Get related event if available
            event_name = None
            if tx.event_id:
                event = db.query(models.Event).filter(models.Event.id == tx.event_id).first()
                if event:
                    event_name = event.title
            
            activity = {
                "id": tx.id,
                "type": activity_type,
                "description": tx.description,
                "points": abs(tx.points),
                "timestamp": tx.timestamp.isoformat() if tx.timestamp else None,
                "event_id": tx.event_id,
                "event_name": event_name
            }
            activities.append(activity)
        
        logging.info(f"Retrieved {len(activities)} activities for user {user_id}")
        return activities
        
    except SQLAlchemyError as e:
        logging.error(f"Database error in get_user_activities: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred when retrieving activities"
        )
        
    except Exception as e:
        logging.error(f"Unexpected error in get_user_activities: {str(e)}", exc_info=True)
        # Return empty list as fallback
        return []


@router.get("/balance", response_model=int)
@safe_api_call
def get_points_balance(
    request: Request,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get current user's points balance.
    """
    try:
        user_id = safe_get_user_id(current_user)
        if user_id is None:
            logging.warning("User ID is None when fetching points balance")
            return 0
            
        points_manager = PointsManager(db)
        balance = points_manager.get_user_points_balance(user_id)
        logging.info(f"Retrieved points balance {balance} for user {user_id}")
        return balance
        
    except SQLAlchemyError as e:
        logging.error(f"Database error in get_points_balance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred when retrieving points balance"
        )
        
    except Exception as e:
        logging.error(f"Unexpected error in get_points_balance: {str(e)}", exc_info=True)
        # Return 0 as a fallback to prevent UI errors
        return 0


@router.get("/transactions", response_model=schemas.PaginatedPointsTransactionResponse)
@safe_api_call
def get_user_transactions(
    request: Request,
    db: Session = Depends(dependencies.get_db),
    skip: int = 0,
    limit: int = 100,
    transaction_type: Optional[str] = None,
    date_from: Optional[datetime] = None,
    date_to: Optional[datetime] = None,
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get current user's points transactions with pagination and filtering.
    
    Parameters:
    - skip: Number of items to skip (for pagination)
    - limit: Maximum number of items to return
    - transaction_type: Filter by transaction type (earned, spent, etc.)
    - date_from: Filter by minimum transaction date
    - date_to: Filter by maximum transaction date
    
    Returns a paginated response with items, total count, and pagination metadata.
    """
    try:
        user_id = safe_get_user_id(current_user)
        if user_id is None:
            logging.warning("User ID is None when fetching transactions")
            return {
                "items": [],
                "total": 0,
                "page": 1,
                "size": limit,
                "pages": 0
            }
        
        # Base query for items
        query = db.query(models.PointsTransaction).filter(
            models.PointsTransaction.user_id == user_id
        )
        
        # Base query for count (for pagination metadata)
        count_query = db.query(func.count(models.PointsTransaction.id)).filter(
            models.PointsTransaction.user_id == user_id
        )
        
        # Apply transaction_type filter
        if transaction_type:
            query = query.filter(models.PointsTransaction.transaction_type == transaction_type)
            count_query = count_query.filter(models.PointsTransaction.transaction_type == transaction_type)
        
        # Apply date_from filter
        if date_from:
            query = query.filter(models.PointsTransaction.transaction_date >= date_from)
            count_query = count_query.filter(models.PointsTransaction.transaction_date >= date_from)
        
        # Apply date_to filter
        if date_to:
            query = query.filter(models.PointsTransaction.transaction_date <= date_to)
            count_query = count_query.filter(models.PointsTransaction.transaction_date <= date_to)
        
        # Get total count for pagination metadata
        total_count = count_query.scalar() or 0
        
        # Apply sorting and pagination
        transactions = query.order_by(
            models.PointsTransaction.transaction_date.desc()
        ).offset(skip).limit(limit).all()
        
        # Calculate pagination metadata
        page_size = limit
        current_page = (skip // page_size) + 1 if page_size > 0 else 1
        total_pages = (total_count + page_size - 1) // page_size if page_size > 0 else 1
        
        logging.info(f"Retrieved {len(transactions)} transactions for user {user_id}")
        
        # Convert SQLAlchemy models to Pydantic models for proper serialization
        transaction_schemas = []
        for transaction in transactions:
            try:
                # Use the utility function for consistent conversion
                transaction_schema = safe_sqlalchemy_to_pydantic(transaction, schemas.PointsTransaction)
                transaction_schemas.append(transaction_schema)
            except ValueError as e:
                logging.error(f"Error converting transaction {transaction.id}: {str(e)}")
                # Skip this transaction if conversion fails
        
        # Return paginated response with properly serialized items
        return {
            "items": transaction_schemas if transaction_schemas else [],
            "total": total_count,
            "page": current_page,
            "size": page_size,
            "pages": total_pages
        }
        
    except SQLAlchemyError as e:
        logging.error(f"Database error in get_user_transactions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred when retrieving transactions"
        )
        
    except Exception as e:
        logging.error(f"Unexpected error in get_user_transactions: {str(e)}", exc_info=True)
        # Log the specific error for debugging
        logging.error(f"Error processing request: {str(e)}", exc_info=True)
        
        # Return empty paginated response as fallback
        return {
            "items": [],
            "total": 0,
            "page": 1,
            "size": limit,
            "pages": 0
        }


@router.get("/users/{user_id}/history", response_model=List[schemas.PointsTransaction])
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
            
            # Convert SQLAlchemy models to Pydantic models for proper serialization
            history = []
            for tx in transactions:
                try:
                    # Use the utility function for consistent conversion
                    transaction_schema = safe_sqlalchemy_to_pydantic(tx, schemas.PointsTransaction)
                    history.append(transaction_schema)
                except ValueError as e:
                    logging.error(f"Error converting transaction {tx.id}: {str(e)}")
                    # Skip this transaction if conversion fails
            
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
        logging.error(f"Error processing request: {str(e)}", exc_info=True)
        # Return empty list as fallback
        return []


@router.post("/award", response_model=schemas.PointsTransaction)
@safe_api_call
def award_points(
    *,
    request: Request,
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
    try:
        # Validate user exists
        user = db.query(models.User).filter(models.User.id == user_id).first()
        if not user:
            logging.error(f"User with ID {user_id} not found when awarding points")
            raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
        
        admin_id = safe_get_user_id(current_user)
        if admin_id is None:
            logging.error("Admin user ID is None when awarding points")
            raise HTTPException(status_code=401, detail="Admin authentication required")
        
        points_manager = PointsManager(db)
        
        transaction = points_manager.award_points(
            user_id=user_id,
            points=points,
            transaction_type="earned",
            description=description,
            event_id=event_id
        )
        
        # Convert SQLAlchemy model to Pydantic model for proper serialization
        try:
            transaction_schema = safe_sqlalchemy_to_pydantic(transaction, schemas.PointsTransaction)
        except ValueError as e:
            logging.error(f"Error converting transaction: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing transaction data"
            )
        
        logging.info(f"Admin {admin_id} awarded {points} points to user {user_id}")
        return transaction_schema
        
    except ValueError as e:
        logging.error(f"Value error in award_points: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
        
    except SQLAlchemyError as e:
        logging.error(f"Database error in award_points: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred when awarding points"
        )
        
    except Exception as e:
        logging.error(f"Unexpected error in award_points: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred when awarding points"
        )


@router.post("/redeem", response_model=schemas.PointsTransaction)
@safe_api_call
def redeem_points(
    *,
    request: Request,
    db: Session = Depends(dependencies.get_db),
    points: int = Body(..., gt=0),
    description: str = Body(...),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Redeem points for the current user.
    """
    try:
        user_id = safe_get_user_id(current_user)
        if user_id is None:
            logging.error("User ID is None when redeeming points")
            raise HTTPException(status_code=401, detail="Authentication required")
        
        points_manager = PointsManager(db)
        
        # Check if user has enough points
        balance = points_manager.get_user_points_balance(user_id)
        if balance < points:
            logging.warning(f"User {user_id} attempted to redeem {points} points but only has {balance}")
            raise HTTPException(status_code=400, detail=f"Not enough points. Current balance: {balance}")
        
        transaction = points_manager.award_points(
            user_id=user_id,
            points=-points,  # Negative points for redemption
            transaction_type="redeemed",
            description=description
        )
        
        # Convert SQLAlchemy model to Pydantic model for proper serialization
        try:
            transaction_schema = safe_sqlalchemy_to_pydantic(transaction, schemas.PointsTransaction)
        except ValueError as e:
            logging.error(f"Error converting transaction: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error processing transaction data"
            )
        
        logging.info(f"User {user_id} redeemed {points} points. New balance: {balance - points}")
        return transaction_schema
        
    except ValueError as e:
        logging.error(f"Value error in redeem_points: {str(e)}")
        raise HTTPException(status_code=404, detail=str(e))
        
    except SQLAlchemyError as e:
        logging.error(f"Database error in redeem_points: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred when redeeming points"
        )
        
    except Exception as e:
        logging.error(f"Unexpected error in redeem_points: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred when redeeming points"
        )


@router.get("/leaderboard", response_model=List[dict])
@safe_api_call
def get_points_leaderboard(
    request: Request,
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
    try:
        from datetime import datetime, timedelta
        from sqlalchemy import func, desc
        
        user_id = safe_get_user_id(current_user)
        if user_id is None:
            logging.warning("User ID is None when fetching leaderboard")
            return []
            
        now = datetime.utcnow()
        
        # Define time period filter
        if time_period == "weekly":
            # Start of current week (Monday)
            start_date = now - timedelta(days=now.weekday(), hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
            logging.info(f"Using weekly time period starting at {start_date}")
        elif time_period == "monthly":
            # Start of current month
            start_date = datetime(now.year, now.month, 1)
            logging.info(f"Using monthly time period starting at {start_date}")
        else:  # all_time or invalid value
            start_date = None
            logging.info("Using all-time period for leaderboard")
        
        # Get users with their points
        try:
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
                for user_id_entry, points in leaderboard_query:
                    user = db.query(models.User).filter(models.User.id == user_id_entry).first()
                    if user:
                        leaderboard.append({
                            "user_id": user.id,
                            "username": user.username,
                            "full_name": getattr(user, "full_name", None),
                            "points": points,
                            "rank": len(leaderboard) + 1,
                            "is_current_user": user.id == user_id
                        })
            else:
                # For all-time leaderboard, use the points manager to get accurate balances
                points_manager = PointsManager(db)
                users = db.query(models.User).filter(models.User.is_active == True).all()
                
                leaderboard = []
                for user in users:
                    try:
                        points = points_manager.get_user_points_balance(user.id)
                        if points > 0:  # Only include users with points
                            leaderboard.append({
                                "user_id": user.id,
                                "username": user.username,
                                "full_name": getattr(user, "full_name", None),
                                "points": points,
                                "is_current_user": user.id == user_id
                            })
                    except Exception as user_error:
                        logging.error(f"Error getting points for user {user.id}: {str(user_error)}")
                        continue
                
                # Sort by points (descending)
                leaderboard.sort(key=lambda x: x["points"], reverse=True)
                
                # Add rank
                for i, entry in enumerate(leaderboard):
                    entry["rank"] = i + 1
                
                # Limit results
                leaderboard = leaderboard[:limit]
            
            # Find current user's rank if not in the top results
            try:
                current_user_in_results = any(entry["user_id"] == user_id for entry in leaderboard)
                
                if not current_user_in_results and user_id is not None:
                    # Get current user's points
                    if start_date:
                        current_user_points = db.query(
                            func.sum(models.PointsTransaction.points)
                        ).filter(
                            models.PointsTransaction.user_id == user_id,
                            models.PointsTransaction.transaction_date >= start_date
                        ).scalar() or 0
                    else:
                        points_manager = PointsManager(db)
                        current_user_points = points_manager.get_user_points_balance(user_id)
                    
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
                            if user.id != user_id:
                                try:
                                    user_points = points_manager.get_user_points_balance(user.id)
                                    if user_points > current_user_points:
                                        higher_ranks += 1
                                except Exception as rank_error:
                                    logging.error(f"Error comparing points for user {user.id}: {str(rank_error)}")
                                    continue
                    
                    # Add current user to the results with their rank
                    if current_user_points > 0:
                        current_user_entry = {
                            "user_id": user_id,
                            "username": current_user.username,
                            "full_name": getattr(current_user, "full_name", None),
                            "points": current_user_points,
                            "rank": higher_ranks + 1,
                            "is_current_user": True
                        }
                        leaderboard.append(current_user_entry)
            except Exception as rank_error:
                logging.error(f"Error calculating user rank: {str(rank_error)}")
                # Continue without adding current user to results
                
            logging.info(f"Retrieved leaderboard with {len(leaderboard)} entries")
            return leaderboard
                
        except SQLAlchemyError as db_error:
            logging.error(f"SQL error in get_points_leaderboard: {str(db_error)}")
            # Fallback to a simpler query if the complex one fails
            simple_result = db.query(models.User).order_by(models.User.id).limit(limit).all()
            
            # Create a basic leaderboard with zero points
            fallback_leaderboard = [
                {
                    "user_id": user.id,
                    "username": user.username,
                    "full_name": getattr(user, "full_name", None),
                    "points": 0,
                    "rank": idx + 1,
                    "is_current_user": user.id == user_id
                }
                for idx, user in enumerate(simple_result)
            ]
            
            logging.info(f"Retrieved fallback leaderboard with {len(fallback_leaderboard)} entries")
            return fallback_leaderboard
            
    except SQLAlchemyError as e:
        logging.error(f"Database error in get_points_leaderboard: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error occurred when retrieving leaderboard"
        )
        
    except Exception as e:
        logging.error(f"Unexpected error in get_points_leaderboard: {str(e)}", exc_info=True)
        # Return empty list as fallback
        return []


@router.get("/stats", response_model=dict)
@safe_api_call
def get_user_points_stats(
    request: Request,
    db: Session = Depends(dependencies.get_db),
    current_user: models.User = Depends(dependencies.get_current_active_user),
) -> Any:
    """
    Get detailed statistics about a user's points.
    
    Returns information about points earned, redeemed, and a breakdown by categories.
    """
    try:
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        user_id = safe_get_user_id(current_user)
        if user_id is None:
            logging.warning("User ID is None when fetching points stats")
            # Return empty stats as fallback
            return {
                "current_balance": 0,
                "total_earned": 0,
                "total_redeemed": 0,
                "earned_this_week": 0,
                "earned_this_month": 0,
                "user_rank": None,
                "event_type_breakdown": [],
                "recent_transactions": []
            }
        
        points_manager = PointsManager(db)
        now = datetime.utcnow()
        
        try:
            # Get current balance
            current_balance = points_manager.get_user_points_balance(user_id)
            logging.info(f"Retrieved current balance {current_balance} for user {user_id}")
            
            # Get total earned and redeemed
            total_earned = db.query(func.sum(models.PointsTransaction.points)).filter(
                models.PointsTransaction.user_id == user_id,
                models.PointsTransaction.transaction_type == "earned"
            ).scalar() or 0
            
            total_redeemed = db.query(func.sum(models.PointsTransaction.points)).filter(
                models.PointsTransaction.user_id == user_id,
                models.PointsTransaction.transaction_type == "redeemed"
            ).scalar() or 0
            
            # Get points earned this week
            week_start = now - timedelta(days=now.weekday(), hours=now.hour, minutes=now.minute, seconds=now.second, microseconds=now.microsecond)
            earned_this_week = db.query(func.sum(models.PointsTransaction.points)).filter(
                models.PointsTransaction.user_id == user_id,
                models.PointsTransaction.transaction_type == "earned",
                models.PointsTransaction.transaction_date >= week_start
            ).scalar() or 0
            
            # Get points earned this month
            month_start = datetime(now.year, now.month, 1)
            earned_this_month = db.query(func.sum(models.PointsTransaction.points)).filter(
                models.PointsTransaction.user_id == user_id,
                models.PointsTransaction.transaction_type == "earned",
                models.PointsTransaction.transaction_date >= month_start
            ).scalar() or 0
            
            # Get breakdown by event type - wrapped in try/except as this join might fail
            event_type_breakdown = []
            try:
                event_points = db.query(
                    models.Event.event_type,
                    func.sum(models.PointsTransaction.points).label("points")
                ).join(
                    models.PointsTransaction,
                    models.PointsTransaction.event_id == models.Event.id
                ).filter(
                    models.PointsTransaction.user_id == user_id,
                    models.PointsTransaction.transaction_type == "earned"
                ).group_by(
                    models.Event.event_type
                ).all()
                
                for event_type, points in event_points:
                    event_type_breakdown.append({
                        "event_type": event_type,
                        "points": points
                    })
            except Exception as event_error:
                logging.error(f"Error getting event breakdown: {str(event_error)}")
                # Continue with empty breakdown
            
            # Get recent transactions
            recent_transactions_data = []
            try:
                recent_transactions = db.query(models.PointsTransaction).filter(
                    models.PointsTransaction.user_id == user_id
                ).order_by(
                    models.PointsTransaction.transaction_date.desc()
                ).limit(5).all()
                
                for transaction in recent_transactions:
                    recent_transactions_data.append({
                        "id": transaction.id,
                        "points": transaction.points,
                        "transaction_type": transaction.transaction_type,
                        "description": transaction.description,
                        "transaction_date": transaction.transaction_date
                    })
            except Exception as tx_error:
                logging.error(f"Error getting recent transactions: {str(tx_error)}")
                # Continue with empty transactions
            
            # Get user rank - use the request parameter to call the enhanced leaderboard endpoint
            user_rank = None
            try:
                leaderboard = get_points_leaderboard(request=request, db=db, limit=1000, current_user=current_user)
                user_rank = next((entry["rank"] for entry in leaderboard if entry["user_id"] == user_id), None)
            except Exception as rank_error:
                logging.error(f"Error getting user rank: {str(rank_error)}")
                # Continue with null rank
            
            stats = {
                "current_balance": current_balance,
                "total_earned": total_earned,
                "total_redeemed": abs(total_redeemed),
                "earned_this_week": earned_this_week,
                "earned_this_month": earned_this_month,
                "user_rank": user_rank,
                "event_type_breakdown": event_type_breakdown,
                "recent_transactions": recent_transactions_data
            }
            
            logging.info(f"Retrieved complete stats for user {user_id}")
            return stats
            
        except SQLAlchemyError as db_error:
            logging.error(f"Database error in get_user_points_stats: {str(db_error)}")
            # Return basic stats with zeros as fallback
            return {
                "current_balance": 0,
                "total_earned": 0,
                "total_redeemed": 0,
                "earned_this_week": 0,
                "earned_this_month": 0,
                "user_rank": None,
                "event_type_breakdown": [],
                "recent_transactions": []
            }
            
    except Exception as e:
        logging.error(f"Unexpected error in get_user_points_stats: {str(e)}", exc_info=True)
        # Return empty stats as fallback
        return {
            "current_balance": 0,
            "total_earned": 0,
            "total_redeemed": 0,
            "earned_this_week": 0,
            "earned_this_month": 0,
            "user_rank": None,
            "event_type_breakdown": [],
            "recent_transactions": []
        }
