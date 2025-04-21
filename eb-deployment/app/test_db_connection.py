"""
Test script to verify database connection and functionality after migration.
This script can be used with both SQLite and PostgreSQL databases.
"""

import os
import sys
import argparse
import logging
from typing import Dict, List, Any, Optional, Union

from sqlalchemy.orm import Session
from sqlalchemy.sql import text

# Add app directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import models and database session
from app.db.session import engine, SessionLocal
from app.models.user import User
from app.models.event import Event
from app.models.registration import Registration
from app.models.badge import Badge
from app.models.points import PointsTransaction
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("db_test")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Test database connection and functionality")
    parser.add_argument(
        "--db-type", 
        choices=["sqlite", "postgresql"],
        help="Database type to test (overrides environment variable)"
    )
    return parser.parse_args()

def get_db_session():
    """Get a database session."""
    db = SessionLocal()
    try:
        return db
    except Exception as e:
        logger.error(f"Failed to create database session: {e}")
        sys.exit(1)

def test_connection():
    """Test database connection."""
    try:
        # Try to connect to the database
        conn = engine.connect()
        conn.close()
        logger.info("✅ Database connection successful")
        return True
    except Exception as e:
        logger.error(f"❌ Database connection failed: {e}")
        return False

def test_query_execution(db: Session):
    """Test query execution."""
    try:
        # Execute a simple query
        result = db.execute(text("SELECT 1"))
        assert result.scalar() == 1
        logger.info("✅ Query execution successful")
        return True
    except Exception as e:
        logger.error(f"❌ Query execution failed: {e}")
        return False

def test_model_queries(db: Session):
    """Test model queries."""
    models = [
        (User, "users"),
        (Event, "events"),
        (Registration, "registrations"),
        (Badge, "badges"),
        (PointsTransaction, "points transactions")
    ]
    
    all_successful = True
    
    for model, name in models:
        try:
            # Count records
            count = db.query(model).count()
            logger.info(f"✅ Found {count} {name} in the database")
        except Exception as e:
            logger.error(f"❌ Failed to query {name}: {e}")
            all_successful = False
    
    return all_successful

def test_relationships(db: Session):
    """Test relationships between models."""
    try:
        # Test User -> Registration relationship
        user = db.query(User).first()
        if user:
            registrations = db.query(Registration).filter(Registration.user_id == user.id).all()
            logger.info(f"✅ User relationship test: Found {len(registrations)} registrations for user {user.id}")
        else:
            logger.warning("⚠️ No users found to test relationships")
        
        # Test Event -> Registration relationship
        event = db.query(Event).first()
        if event:
            registrations = db.query(Registration).filter(Registration.event_id == event.id).all()
            logger.info(f"✅ Event relationship test: Found {len(registrations)} registrations for event {event.id}")
        else:
            logger.warning("⚠️ No events found to test relationships")
        
        return True
    except Exception as e:
        logger.error(f"❌ Relationship test failed: {e}")
        return False

def run_tests():
    """Run all database tests."""
    logger.info(f"Testing database connection to: {settings.SQLALCHEMY_DATABASE_URI}")
    
    # Test connection
    if not test_connection():
        return False
    
    # Get database session
    db = get_db_session()
    
    # Run tests
    tests = [
        ("Query execution", lambda: test_query_execution(db)),
        ("Model queries", lambda: test_model_queries(db)),
        ("Relationships", lambda: test_relationships(db))
    ]
    
    all_passed = True
    for name, test_func in tests:
        logger.info(f"Running test: {name}")
        if not test_func():
            all_passed = False
    
    # Clean up
    db.close()
    
    return all_passed

def main():
    """Main entry point."""
    args = parse_args()
    
    # Override database type if specified
    if args.db_type:
        os.environ["DATABASE_TYPE"] = args.db_type
        logger.info(f"Using database type: {args.db_type}")
    
    # Run tests
    success = run_tests()
    
    if success:
        logger.info("🎉 All database tests passed!")
        return 0
    else:
        logger.error("❌ Some database tests failed. Check the logs for details.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
