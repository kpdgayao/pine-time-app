"""
Simple script to verify PostgreSQL connection and basic functionality.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("verify_postgres")

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import application components
from app.db.session import SessionLocal
from app.models.user import User
from app.core.config import settings

def main():
    """Verify PostgreSQL connection and basic functionality."""
    try:
        # Print database URI (hiding password)
        db_uri = settings.SQLALCHEMY_DATABASE_URI
        if "postgresql" in db_uri:
            print(f"Using PostgreSQL database")
        else:
            print(f"Using SQLite database: {db_uri}")
        
        # Create session
        print("Creating database session...")
        db = SessionLocal()
        
        # Test connection with a simple query
        print("Testing database connection...")
        user_count = db.query(User).count()
        print(f"User count: {user_count}")
        
        # Get first user
        print("Fetching first user...")
        user = db.query(User).first()
        if user:
            print(f"Found user: ID={user.id}, Username={user.username}, Email={user.email}")
        else:
            print("No users found in database")
        
        # Close session
        db.close()
        print("Database connection test completed successfully!")
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
