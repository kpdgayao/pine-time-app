"""
Initialize SQLite database with tables and sample data.
This script creates all the required tables in the SQLite database
and populates them with some sample data for testing the migration.
"""

import os
import sys
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_init")

# Import SQLAlchemy components
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.user import User
from app.models.event import Event
from app.models.registration import Registration
from app.models.badge import Badge
from app.models.points import PointsTransaction

# Create engine for SQLite
sqlite_url = os.getenv("SQLITE_DATABASE_URI", "sqlite:///./pine_time.db")
engine = create_engine(sqlite_url, connect_args={"check_same_thread": False})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initialize database with tables and sample data."""
    logger.info(f"Initializing SQLite database at: {sqlite_url}")
    
    # Create all tables
    logger.info("Creating tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tables created successfully.")
    
    # Create session
    db = SessionLocal()
    
    try:
        # Check if data already exists
        if db.query(User).first():
            logger.info("Database already contains data. Skipping sample data creation.")
            return
        
        # Create sample data
        logger.info("Creating sample data...")
        
        # Create users
        logger.info("Creating users...")
        admin_user = User(
            email="admin@pinetimeexperience.com",
            username="admin",
            full_name="Admin User",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "admin"
            is_active=True,
            is_superuser=True,
            user_type="admin"
        )
        
        regular_user = User(
            email="user@example.com",
            username="user",
            full_name="Regular User",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "admin"
            is_active=True,
            is_superuser=False,
            user_type="regular"
        )
        
        business_user = User(
            email="business@example.com",
            username="business",
            full_name="Business User",
            hashed_password="$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",  # "admin"
            is_active=True,
            is_superuser=False,
            user_type="business"
        )
        
        db.add_all([admin_user, regular_user, business_user])
        db.commit()
        
        # Create events
        logger.info("Creating events...")
        now = datetime.utcnow()
        
        trivia_night = Event(
            title="Trivia Night at Pine Time",
            description="Join us for a fun night of trivia at Pine Time Experience Baguio!",
            event_type="trivia",
            location="Pine Time Cafe, Baguio City",
            start_time=now + timedelta(days=7),
            end_time=now + timedelta(days=7, hours=3),
            max_participants=30,
            points_reward=100,
            is_active=True,
            image_url="https://example.com/trivia.jpg",
            price=0.0
        )
        
        game_night = Event(
            title="Board Game Night",
            description="Enjoy a variety of board games with friends and family!",
            event_type="game_night",
            location="Pine Time Cafe, Baguio City",
            start_time=now + timedelta(days=14),
            end_time=now + timedelta(days=14, hours=4),
            max_participants=20,
            points_reward=150,
            is_active=True,
            image_url="https://example.com/games.jpg",
            price=50.0
        )
        
        murder_mystery = Event(
            title="Murder Mystery Dinner",
            description="Solve a murder mystery while enjoying a delicious dinner!",
            event_type="murder_mystery",
            location="Pine Time Restaurant, Baguio City",
            start_time=now + timedelta(days=21),
            end_time=now + timedelta(days=21, hours=5),
            max_participants=15,
            points_reward=200,
            is_active=True,
            image_url="https://example.com/mystery.jpg",
            price=100.0
        )
        
        db.add_all([trivia_night, game_night, murder_mystery])
        db.commit()
        
        # Create registrations
        logger.info("Creating registrations...")
        reg1 = Registration(
            user_id=regular_user.id,
            event_id=trivia_night.id,
            registration_date=now - timedelta(days=1),
            status="registered",
            payment_status="completed"
        )
        
        reg2 = Registration(
            user_id=regular_user.id,
            event_id=game_night.id,
            registration_date=now - timedelta(days=2),
            status="registered",
            payment_status="pending"
        )
        
        reg3 = Registration(
            user_id=business_user.id,
            event_id=murder_mystery.id,
            registration_date=now - timedelta(days=3),
            status="registered",
            payment_status="completed"
        )
        
        db.add_all([reg1, reg2, reg3])
        db.commit()
        
        # Create badges
        logger.info("Creating badges...")
        badge1 = Badge(
            user_id=regular_user.id,
            badge_type="event_master",
            name="Event Master",
            description="Attended 5 events",
            image_url="https://example.com/badge1.jpg",
            earned_date=now - timedelta(days=30)
        )
        
        badge2 = Badge(
            user_id=regular_user.id,
            badge_type="trivia_champion",
            name="Trivia Champion",
            description="Won a trivia night event",
            image_url="https://example.com/badge2.jpg",
            earned_date=now - timedelta(days=15)
        )
        
        db.add_all([badge1, badge2])
        db.commit()
        
        # Create points transactions
        logger.info("Creating points transactions...")
        pt1 = PointsTransaction(
            user_id=regular_user.id,
            points=100,
            transaction_type="earned",
            description="Attended Trivia Night",
            event_id=trivia_night.id,
            transaction_date=now - timedelta(days=45)
        )
        
        pt2 = PointsTransaction(
            user_id=regular_user.id,
            points=150,
            transaction_type="earned",
            description="Won Game Night",
            event_id=game_night.id,
            transaction_date=now - timedelta(days=30)
        )
        
        pt3 = PointsTransaction(
            user_id=business_user.id,
            points=200,
            transaction_type="earned",
            description="Hosted Murder Mystery",
            event_id=murder_mystery.id,
            transaction_date=now - timedelta(days=15)
        )
        
        db.add_all([pt1, pt2, pt3])
        db.commit()
        
        logger.info("Sample data created successfully.")
    
    except Exception as e:
        logger.error(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
