#!/usr/bin/env python3
"""
Script to run the points data reset.
This script provides a command-line interface to reset the points transactions.
"""
import sys
import os
import logging
import argparse
from typing import Optional

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.db.session import get_db
from reset_points_data import reset_points_data
from clean_points_transactions import clean_and_reset_points_transactions, get_database_session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Reset points transactions in the database")
    parser.add_argument(
        "--clean-only", 
        action="store_true", 
        help="Only clean the points transactions without adding sample data"
    )
    parser.add_argument(
        "--confirm", 
        action="store_true", 
        help="Skip confirmation prompt"
    )
    return parser.parse_args()

def confirm_reset() -> bool:
    """Ask for confirmation before resetting data."""
    response = input("This will delete all existing points transactions. Continue? (y/n): ")
    return response.lower() in ["y", "yes"]

def main() -> None:
    """Main function to run the script."""
    try:
        # Parse command line arguments
        args = parse_args()
        
        # Ask for confirmation unless --confirm flag is used
        if not args.confirm and not confirm_reset():
            logger.info("Operation cancelled by user")
            return
        
        # Get database session
        db = get_database_session()
        
        try:
            if args.clean_only:
                # Only clean the points transactions
                clean_and_reset_points_transactions(db)
                logger.info("Points transactions have been cleaned (without adding sample data)")
            else:
                # Reset points data with sample data
                reset_points_data(db)
                logger.info("Points transactions have been reset with sample data")
        finally:
            # Close the database session
            db.close()
            
        logger.info("Operation completed successfully")
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
