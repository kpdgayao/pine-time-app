#!/usr/bin/env python3
"""
Comprehensive utility for managing points transactions in the Pine Time application.
This script provides a command-line interface for viewing, resetting, and managing points data.

Usage:
  python manage_points.py --display  # Display current points data
  python manage_points.py --reset    # Reset points data with sample data
  python manage_points.py --clean    # Delete all points transactions
  python manage_points.py --summary  # Show points summary by user
"""
import sys
import os
import logging
import argparse
import json
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text, func

from app.db.session import get_db
from app.core.config import settings
from app.models.points import PointsTransaction
from app.models.user import User

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Sample points transactions data
SAMPLE_POINTS_TRANSACTIONS = [
    {
        "id": 1,
        "user_id": 2,
        "points": 100,
        "transaction_type": "earned",
        "description": "Attended Trivia Night",
        "event_id": 1,
        "transaction_date": "2025-02-12 04:52:34.36538",
        "admin_id": None
    },
    {
        "id": 2,
        "user_id": 2,
        "points": 150,
        "transaction_type": "earned",
        "description": "Won Game Night",
        "event_id": 2,
        "transaction_date": "2025-02-27 04:52:34.36538",
        "admin_id": None
    },
    {
        "id": 3,
        "user_id": 3,
        "points": 200,
        "transaction_type": "earned",
        "description": "Hosted Murder Mystery",
        "event_id": 3,
        "transaction_date": "2025-03-14 04:52:34.36538",
        "admin_id": None
    },
    {
        "id": 4,
        "user_id": 4,
        "points": 50,
        "transaction_type": "earned",
        "description": "Created event: test",
        "event_id": 4,
        "transaction_date": "2025-04-12 08:21:19.509775",
        "admin_id": None
    },
    {
        "id": 5,
        "user_id": 4,
        "points": 50,
        "transaction_type": "earned",
        "description": "Created event: Anime Tribianaito",
        "event_id": 5,
        "transaction_date": "2025-04-18 14:15:50.51361",
        "admin_id": None
    },
    {
        "id": 6,
        "user_id": 4,
        "points": 50,
        "transaction_type": "earned",
        "description": "Created event: test event 2",
        "event_id": 6,
        "transaction_date": "2025-04-19 07:13:13.888097",
        "admin_id": None
    },
    {
        "id": 7,
        "user_id": 4,
        "points": 50,
        "transaction_type": "earned",
        "description": "Created event: Quiz Bee: Pop Culture Edition",
        "event_id": 7,
        "transaction_date": "2025-04-19 09:06:38.536564",
        "admin_id": None
    },
    {
        "id": 8,
        "user_id": 2,
        "points": 30,
        "transaction_type": "event_attendance",
        "description": "Attended 'Til Death Do Us Part - Valentine's Murder Mystery Night",
        "event_id": 8,
        "transaction_date": "2025-02-15 21:10:00",
        "admin_id": None
    },
    {
        "id": 9,
        "user_id": 3,
        "points": 30,
        "transaction_type": "event_attendance",
        "description": "Attended 'Til Death Do Us Part - Valentine's Murder Mystery Night",
        "event_id": 8,
        "transaction_date": "2025-02-15 21:10:00",
        "admin_id": None
    },
    {
        "id": 10,
        "user_id": 5,
        "points": 30,
        "transaction_type": "event_attendance",
        "description": "Attended 'Til Death Do Us Part - Valentine's Murder Mystery Night",
        "event_id": 8,
        "transaction_date": "2025-02-15 21:10:00",
        "admin_id": None
    },
    {
        "id": 11,
        "user_id": 4,
        "points": 30,
        "transaction_type": "event_attendance",
        "description": "Attended 'Til Death Do Us Part - Valentine's Murder Mystery Night",
        "event_id": 8,
        "transaction_date": "2025-02-15 21:10:00",
        "admin_id": None
    },
    {
        "id": 12,
        "user_id": 6,
        "points": 30,
        "transaction_type": "event_attendance",
        "description": "Attended 'Til Death Do Us Part - Valentine's Murder Mystery Night",
        "event_id": 8,
        "transaction_date": "2025-02-15 21:10:00",
        "admin_id": None
    }
]

def get_database_session() -> Session:
    """
    Get a database session.
    
    Returns:
        Session: A SQLAlchemy database session
    
    Raises:
        Exception: If database connection fails
    """
    try:
        # Create a new session
        db = next(get_db())
        return db
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise

def delete_all_points_transactions(db: Session) -> int:
    """
    Delete all points transactions from the database.
    
    Args:
        db: Database session
        
    Returns:
        int: Number of deleted transactions
        
    Raises:
        Exception: If deletion fails
    """
    try:
        count = db.query(PointsTransaction).delete()
        db.commit()
        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete points transactions: {str(e)}")
        raise

def add_sample_points_transactions(db: Session, transactions: List[Dict[str, Any]]) -> None:
    """
    Add sample points transactions to the database.
    
    Args:
        db: Database session
        transactions: List of transaction data dictionaries
        
    Raises:
        Exception: If adding transactions fails
    """
    try:
        for tx_data in transactions:
            # Create a new transaction object
            tx = PointsTransaction(
                user_id=tx_data["user_id"],
                points=tx_data["points"],
                transaction_type=tx_data["transaction_type"],
                description=tx_data["description"],
                event_id=tx_data["event_id"],
                transaction_date=datetime.fromisoformat(tx_data["transaction_date"].replace(" ", "T")),
                admin_id=tx_data.get("admin_id")
            )
            db.add(tx)
        
        db.commit()
        logger.info(f"Added {len(transactions)} sample points transactions")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to add sample points transactions: {str(e)}")
        raise

def get_points_transactions(db: Session) -> List[Dict[str, Any]]:
    """
    Get all points transactions from the database.
    
    Args:
        db: Database session
        
    Returns:
        List of transaction dictionaries
        
    Raises:
        Exception: If fetching transactions fails
    """
    try:
        transactions = db.query(PointsTransaction).all()
        result = []
        for tx in transactions:
            result.append({
                "id": tx.id,
                "user_id": tx.user_id,
                "points": tx.points,
                "transaction_type": tx.transaction_type,
                "description": tx.description,
                "event_id": tx.event_id,
                "transaction_date": tx.transaction_date.isoformat(),
                "admin_id": tx.admin_id
            })
        return result
    except Exception as e:
        logger.error(f"Failed to get points transactions: {str(e)}")
        raise

def get_user_points_summary(db: Session) -> Dict[int, int]:
    """
    Get a summary of points per user.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary mapping user IDs to point totals
        
    Raises:
        Exception: If fetching summary fails
    """
    try:
        # Use SQLAlchemy's aggregation functions for better performance
        results = db.query(
            PointsTransaction.user_id,
            func.sum(PointsTransaction.points).label("total_points")
        ).group_by(PointsTransaction.user_id).all()
        
        # Convert to dictionary
        user_points = {user_id: total_points for user_id, total_points in results}
        return user_points
    except Exception as e:
        logger.error(f"Failed to get user points summary: {str(e)}")
        raise

def get_transaction_type_summary(db: Session) -> Dict[str, int]:
    """
    Get a summary of points by transaction type.
    
    Args:
        db: Database session
        
    Returns:
        Dictionary mapping transaction types to point totals
        
    Raises:
        Exception: If fetching summary fails
    """
    try:
        # Use SQLAlchemy's aggregation functions
        results = db.query(
            PointsTransaction.transaction_type,
            func.sum(PointsTransaction.points).label("total_points")
        ).group_by(PointsTransaction.transaction_type).all()
        
        # Convert to dictionary
        type_points = {tx_type: total_points for tx_type, total_points in results}
        return type_points
    except Exception as e:
        logger.error(f"Failed to get transaction type summary: {str(e)}")
        raise

def get_user_names(db: Session, user_ids: List[int]) -> Dict[int, str]:
    """
    Get user names for a list of user IDs.
    
    Args:
        db: Database session
        user_ids: List of user IDs
        
    Returns:
        Dictionary mapping user IDs to user names
        
    Raises:
        Exception: If fetching user names fails
    """
    try:
        users = db.query(User).filter(User.id.in_(user_ids)).all()
        user_names = {}
        for user in users:
            # Use full_name if available, otherwise use email
            name = user.full_name if user.full_name else user.email
            user_names[user.id] = name
        return user_names
    except Exception as e:
        logger.error(f"Failed to get user names: {str(e)}")
        # Return empty dict as fallback
        return {}

def reset_points_data(db: Session) -> None:
    """
    Reset points transactions with the sample data.
    
    Args:
        db: Database session
        
    Raises:
        Exception: If reset fails
    """
    try:
        # Delete all existing transactions
        count = delete_all_points_transactions(db)
        logger.info(f"Deleted {count} existing points transactions")
        
        # Add sample transactions
        add_sample_points_transactions(db, SAMPLE_POINTS_TRANSACTIONS)
        
        logger.info("Points transactions have been reset with sample data")
    except Exception as e:
        logger.error(f"Failed to reset points data: {str(e)}")
        raise

def display_points_data(db: Session) -> None:
    """
    Display current points data in a formatted way.
    
    Args:
        db: Database session
        
    Raises:
        Exception: If display fails
    """
    try:
        # Get all points transactions
        transactions = get_points_transactions(db)
        
        # Display transactions
        print("\nCurrent Points Transactions:")
        print("===========================")
        print(json.dumps(transactions, indent=2))
        print(f"\nTotal: {len(transactions)} transactions")
        
        # Display user points summary
        user_points = get_user_points_summary(db)
        
        # Try to get user names
        try:
            user_names = get_user_names(db, list(user_points.keys()))
        except Exception:
            user_names = {}
        
        print("\nPoints Per User:")
        print("===============")
        for user_id, points in sorted(user_points.items(), key=lambda x: x[1], reverse=True):
            user_name = user_names.get(user_id, f"User {user_id}")
            print(f"{user_name}: {points} points")
        
        # Display transaction type summary
        type_points = get_transaction_type_summary(db)
        print("\nPoints By Transaction Type:")
        print("==========================")
        for tx_type, points in sorted(type_points.items(), key=lambda x: x[1], reverse=True):
            print(f"{tx_type}: {points} points")
    except Exception as e:
        logger.error(f"Failed to display points data: {str(e)}")
        raise

def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description="Manage points transactions in the Pine Time application",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python manage_points.py --display  # Display current points data
  python manage_points.py --reset    # Reset points data with sample data
  python manage_points.py --clean    # Delete all points transactions
  python manage_points.py --summary  # Show points summary by user
"""
    )
    
    action_group = parser.add_mutually_exclusive_group(required=True)
    action_group.add_argument(
        "--display", 
        action="store_true", 
        help="Display current points data"
    )
    action_group.add_argument(
        "--reset", 
        action="store_true", 
        help="Reset points data with sample data"
    )
    action_group.add_argument(
        "--clean", 
        action="store_true", 
        help="Delete all points transactions"
    )
    action_group.add_argument(
        "--summary", 
        action="store_true", 
        help="Show points summary by user"
    )
    
    parser.add_argument(
        "--confirm", 
        action="store_true", 
        help="Skip confirmation prompt for destructive operations"
    )
    
    return parser.parse_args()

def confirm_operation(operation: str) -> bool:
    """
    Ask for confirmation before performing a destructive operation.
    
    Args:
        operation: Description of the operation
        
    Returns:
        bool: True if confirmed, False otherwise
    """
    response = input(f"This will {operation}. Continue? (y/n): ")
    return response.lower() in ["y", "yes"]

def main() -> None:
    """
    Main function to run the script.
    """
    try:
        # Parse command line arguments
        args = parse_args()
        
        # Get database session
        db = get_database_session()
        
        try:
            if args.display:
                # Display current points data
                display_points_data(db)
            
            elif args.summary:
                # Show points summary by user
                user_points = get_user_points_summary(db)
                
                # Try to get user names
                try:
                    user_names = get_user_names(db, list(user_points.keys()))
                except Exception:
                    user_names = {}
                
                print("\nPoints Summary By User:")
                print("======================")
                for user_id, points in sorted(user_points.items(), key=lambda x: x[1], reverse=True):
                    user_name = user_names.get(user_id, f"User {user_id}")
                    print(f"{user_name}: {points} points")
                
                # Display transaction type summary
                type_points = get_transaction_type_summary(db)
                print("\nPoints Summary By Transaction Type:")
                print("==================================")
                for tx_type, points in sorted(type_points.items(), key=lambda x: x[1], reverse=True):
                    print(f"{tx_type}: {points} points")
            
            elif args.reset:
                # Ask for confirmation unless --confirm flag is used
                if not args.confirm and not confirm_operation("reset all points transactions with sample data"):
                    logger.info("Operation cancelled by user")
                    return
                
                # Reset points data
                reset_points_data(db)
                
                # Display updated points data
                display_points_data(db)
            
            elif args.clean:
                # Ask for confirmation unless --confirm flag is used
                if not args.confirm and not confirm_operation("delete all points transactions"):
                    logger.info("Operation cancelled by user")
                    return
                
                # Delete all points transactions
                count = delete_all_points_transactions(db)
                logger.info(f"Deleted {count} points transactions")
                
                print(f"\nDeleted {count} points transactions")
                print("Points transactions have been cleaned up")
        
        finally:
            # Close the database session
            db.close()
            
        logger.info("Operation completed successfully")
    
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
