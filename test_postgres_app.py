"""
Test script to verify application functionality with PostgreSQL.
This script tests various database operations using the application's models
to ensure everything works correctly with the PostgreSQL database.
"""

import os
import sys
import logging
import traceback
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("postgres_app_test.log")
    ]
)
logger = logging.getLogger("postgres_app_test")

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import application components
try:
    from app.db.session import SessionLocal
    from app.models.user import User
    from app.models.event import Event
    from app.models.registration import Registration
    from app.models.badge import Badge
    from app.models.points import PointsTransaction
    from app.core.config import settings
    
    logger.info("Successfully imported application components")
except Exception as e:
    logger.error(f"Error importing application components: {e}")
    logger.error(traceback.format_exc())
    sys.exit(1)

def test_database_connection():
    """Test basic database connection."""
    try:
        # Create session
        db = SessionLocal()
        
        # Test connection
        logger.info("Testing database connection...")
        logger.info(f"Database type: {'PostgreSQL' if 'postgresql' in settings.SQLALCHEMY_DATABASE_URI else 'SQLite'}")
        
        # Try a simple query
        user_count = db.query(User).count()
        logger.info(f"User count: {user_count}")
        
        db.close()
        logger.info("Database connection test passed!")
        return True
    except Exception as e:
        logger.error(f"Database connection test failed: {e}")
        logger.error(traceback.format_exc())
        return False

def test_read_operations():
    """Test read operations on all models."""
    try:
        # Create session
        db = SessionLocal()
        
        # Test User model
        users = db.query(User).all()
        logger.info(f"Found {len(users)} users")
        if users:
            logger.info(f"First user: ID={users[0].id}, Username={users[0].username}")
        
        # Test Event model
        events = db.query(Event).all()
        logger.info(f"Found {len(events)} events")
        if events:
            logger.info(f"First event: ID={events[0].id}, Title={events[0].title}")
        
        # Test Registration model
        registrations = db.query(Registration).all()
        logger.info(f"Found {len(registrations)} registrations")
        
        # Test Badge model
        badges = db.query(Badge).all()
        logger.info(f"Found {len(badges)} badges")
        
        # Test PointsTransaction model
        points = db.query(PointsTransaction).all()
        logger.info(f"Found {len(points)} points transactions")
        
        db.close()
        logger.info("Read operations test passed!")
        return True
    except Exception as e:
        logger.error(f"Read operations test failed: {e}")
        logger.error(traceback.format_exc())
        return False

def test_relationships():
    """Test relationship navigation between models."""
    try:
        # Create session
        db = SessionLocal()
        
        # Test User -> Registrations relationship
        user = db.query(User).first()
        if user:
            logger.info(f"User {user.username} has {len(user.registrations) if hasattr(user, 'registrations') else 'unknown'} registrations")
            
            # Test User -> Badges relationship
            logger.info(f"User {user.username} has {len(user.badges) if hasattr(user, 'badges') else 'unknown'} badges")
            
            # Test User -> PointsTransactions relationship
            logger.info(f"User {user.username} has {len(user.points_transactions) if hasattr(user, 'points_transactions') else 'unknown'} points transactions")
        else:
            logger.warning("No users found for relationship testing")
        
        # Test Event -> Registrations relationship
        event = db.query(Event).first()
        if event:
            logger.info(f"Event {event.title} has {len(event.registrations) if hasattr(event, 'registrations') else 'unknown'} registrations")
        else:
            logger.warning("No events found for relationship testing")
        
        db.close()
        logger.info("Relationship navigation test passed!")
        return True
    except Exception as e:
        logger.error(f"Relationship navigation test failed: {e}")
        logger.error(traceback.format_exc())
        return False

def test_write_operations():
    """Test write operations (create, update, delete)."""
    try:
        # Create session
        db = SessionLocal()
        
        # Check if test user already exists
        existing_user = db.query(User).filter(User.username == "testuser").first()
        if existing_user:
            logger.info(f"Test user already exists with ID: {existing_user.id}, deleting first")
            db.delete(existing_user)
            db.commit()
        
        # Create a test user
        test_user = User(
            email="test@example.com",
            username="testuser",
            full_name="Test User",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "admin"
            is_active=True,
            is_superuser=False,
            user_type="test"
        )
        
        db.add(test_user)
        db.commit()
        db.refresh(test_user)
        logger.info(f"Created test user with ID: {test_user.id}")
        
        # Update the test user
        test_user.full_name = "Updated Test User"
        db.commit()
        db.refresh(test_user)
        logger.info(f"Updated test user: {test_user.full_name}")
        
        # Delete the test user
        db.delete(test_user)
        db.commit()
        logger.info("Deleted test user")
        
        # Verify deletion
        deleted_user = db.query(User).filter(User.username == "testuser").first()
        if deleted_user is None:
            logger.info("User deletion verified")
        else:
            logger.error("User deletion failed")
        
        db.close()
        logger.info("Write operations test passed!")
        return True
    except Exception as e:
        logger.error(f"Write operations test failed: {e}")
        logger.error(traceback.format_exc())
        return False

def main():
    """Main test function."""
    try:
        # Print environment information
        logger.info(f"Testing PostgreSQL connection and functionality")
        logger.info(f"Database URI: {settings.SQLALCHEMY_DATABASE_URI.replace(settings.POSTGRES_PASSWORD, '********') if hasattr(settings, 'POSTGRES_PASSWORD') else settings.SQLALCHEMY_DATABASE_URI}")
        
        # Run tests
        connection_ok = test_database_connection()
        if not connection_ok:
            logger.error("Database connection test failed, aborting further tests")
            return 1
        
        read_ok = test_read_operations()
        relationships_ok = test_relationships()
        write_ok = test_write_operations()
        
        # Check results
        if connection_ok and read_ok and relationships_ok and write_ok:
            logger.info("All tests passed! PostgreSQL migration is working correctly.")
            return 0
        else:
            logger.error("Some tests failed. Check the logs for details.")
            return 1
    
    except Exception as e:
        logger.error(f"Test failed with unexpected error: {e}")
        logger.error(traceback.format_exc())
        return 1

if __name__ == "__main__":
    sys.exit(main())
