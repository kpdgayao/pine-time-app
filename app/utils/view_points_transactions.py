#!/usr/bin/env python3
"""
Utility script to view current points transactions in the database.
This script displays all points transactions in a formatted table.
"""
import sys
import os
import logging
from typing import List, Dict, Any
from datetime import datetime
import json

# Add the parent directory to the path so we can import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.points import PointsTransaction
from clean_points_transactions import get_database_session, list_all_points_transactions

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

def format_points_transactions(transactions: List[Dict[str, Any]]) -> str:
    """Format points transactions as a readable string."""
    if not transactions:
        return "No points transactions found."
    
    # Convert to JSON for better formatting
    return json.dumps(transactions, indent=2, default=str)

def main():
    """Main function to run the script."""
    try:
        # Get database session
        db = get_database_session()
        
        try:
            # Get all points transactions
            transactions = list_all_points_transactions(db)
            
            # Format and print transactions
            formatted_transactions = format_points_transactions(transactions)
            print("\nCurrent Points Transactions:")
            print("===========================")
            print(formatted_transactions)
            print(f"\nTotal: {len(transactions)} transactions")
            
            # Calculate points per user
            user_points = {}
            for tx in transactions:
                user_id = tx["user_id"]
                points = tx["points"]
                user_points[user_id] = user_points.get(user_id, 0) + points
            
            print("\nPoints Per User:")
            print("===============")
            for user_id, points in sorted(user_points.items()):
                print(f"User {user_id}: {points} points")
            
        finally:
            # Close the database session
            db.close()
            
    except Exception as e:
        logger.error(f"Script failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
