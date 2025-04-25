#!/usr/bin/env python3
"""
Utility script to clean up points transactions.
This script can be used to reset or modify points transactions in the database.
"""
import sys
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text

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

def get_database_session() -> Session:
    """Get a database session."""
    try:
        # Create a new session
        db = next(get_db())
        return db
    except Exception as e:
        logger.error(f"Failed to connect to database: {str(e)}")
        raise

def list_all_points_transactions(db: Session) -> List[Dict[str, Any]]:
    """List all points transactions in the database."""
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
                "transaction_date": tx.transaction_date,
                "admin_id": tx.admin_id
            })
        return result
    except Exception as e:
        logger.error(f"Failed to list points transactions: {str(e)}")
        raise

def delete_all_points_transactions(db: Session) -> int:
    """Delete all points transactions from the database."""
    try:
        count = db.query(PointsTransaction).delete()
        db.commit()
        return count
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to delete points transactions: {str(e)}")
        raise

def reset_sequence(db: Session, table_name: str) -> None:
    """Reset the sequence for a table's primary key.
    
    In PostgreSQL, the sequence name can vary based on the table definition.
    This function attempts to find the correct sequence name and reset it.
    """
    try:
        # First, try to get the actual sequence name from PostgreSQL information schema
        result = db.execute(text(
            """SELECT pg_get_serial_sequence(:table_name, 'id') AS seq_name"""), 
            {"table_name": table_name}
        ).fetchone()
        
        if result and result.seq_name:
            sequence_name = result.seq_name
            logger.info(f"Found sequence name: {sequence_name}")
        else:
            # Fallback to common naming patterns
            sequence_name = f"{table_name}_id_seq"
            logger.warning(f"Could not determine sequence name, using fallback: {sequence_name}")
        
        # Reset the sequence
        db.execute(text(f"ALTER SEQUENCE {sequence_name} RESTART WITH 1"))
        db.commit()
        logger.info(f"Reset sequence for {table_name}")
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to reset sequence for {table_name}: {str(e)}")
        # Instead of raising the error, log it and continue
        logger.warning("Continuing without resetting sequence")

def add_sample_points_transactions(db: Session, transactions: List[Dict[str, Any]]) -> None:
    """Add sample points transactions to the database."""
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

def clean_and_reset_points_transactions(db: Session) -> None:
    """Clean up and reset points transactions."""
    try:
        # Delete all existing transactions
        count = delete_all_points_transactions(db)
        logger.info(f"Deleted {count} points transactions")
        
        # Reset the sequence
        reset_sequence(db, "points_transaction")
        
        logger.info("Points transactions have been cleaned up and reset")
    except Exception as e:
        logger.error(f"Failed to clean up points transactions: {str(e)}")
        raise

def main():
    """Main function to run the script."""
    try:
        # Get database session
        db = get_database_session()
        
        # Clean up and reset points transactions
        clean_and_reset_points_transactions(db)
        
        logger.info("Points transactions cleanup completed successfully")
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        sys.exit(1)
    finally:
        # Close the database session
        if 'db' in locals():
            db.close()

if __name__ == "__main__":
    main()
