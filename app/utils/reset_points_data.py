#!/usr/bin/env python3
"""
Script to reset points transactions data with the provided sample data.
This script deletes all existing points transactions and adds back the sample data.
"""
import sys
import os
import logging
from datetime import datetime
from typing import List, Dict, Any

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.points import PointsTransaction
from clean_points_transactions import (
    get_database_session,
    delete_all_points_transactions,
    reset_sequence,
    add_sample_points_transactions
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Sample points transactions data provided by the user
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

def reset_points_data(db: Session) -> None:
    """Reset points transactions with the sample data."""
    try:
        # Delete all existing transactions
        count = delete_all_points_transactions(db)
        logger.info(f"Deleted {count} existing points transactions")
        
        try:
            # Try to reset the sequence, but continue even if it fails
            reset_sequence(db, "points_transaction")
        except Exception as e:
            logger.warning(f"Could not reset sequence, but continuing: {str(e)}")
        
        # Add sample transactions
        add_sample_points_transactions(db, SAMPLE_POINTS_TRANSACTIONS)
        
        logger.info("Points transactions have been reset with sample data")
    except Exception as e:
        logger.error(f"Failed to reset points data: {str(e)}")
        raise

def main():
    """Main function to run the script."""
    try:
        # Get database session
        db = get_database_session()
        
        # Reset points data
        reset_points_data(db)
        
        logger.info("Points data reset completed successfully")
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        sys.exit(1)
    finally:
        # Close the database session
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    main()
