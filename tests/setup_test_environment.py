"""
Test Environment Setup Script for Pine Time App

This script sets up a complete test environment for the Pine Time application,
including database initialization, test data creation, and API verification.

Usage:
    python setup_test_environment.py [--reset-db] [--create-test-users] [--verify-api]
"""

import os
import sys
import argparse
import logging
import psycopg2
from psycopg2.extras import RealDictCursor
import requests
import json
from datetime import datetime, timedelta
import random
import string
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_setup.log")
    ]
)
logger = logging.getLogger("test_setup")

# Load environment variables
load_dotenv()

def get_postgres_connection():
    """
    Create a PostgreSQL connection.
    
    Returns:
        Connection: Database connection
    """
    # Get connection parameters from environment variables
    server = os.getenv("POSTGRES_SERVER", "localhost")
    port = os.getenv("POSTGRES_PORT", "5432")
    user = os.getenv("POSTGRES_USER", "postgres")
    password = os.getenv("POSTGRES_PASSWORD", "")
    db = os.getenv("POSTGRES_DB", "pine_time")
    
    # Create connection
    conn = psycopg2.connect(
        host=server,
        port=port,
        user=user,
        password=password,
        dbname=db,
        cursor_factory=RealDictCursor
    )
    
    # Set isolation level to autocommit
    conn.set_session(autocommit=True)
    
    logger.info(f"Connected to PostgreSQL database: {db} on {server}:{port}")
    return conn

def reset_database(conn):
    """
    Reset the database by truncating all tables and resetting sequences.
    
    Args:
        conn: Database connection
    """
    cursor = conn.cursor()
    
    try:
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        
        tables = [row["table_name"] for row in cursor.fetchall()]
        
        # Disable foreign key constraints
        cursor.execute("SET session_replication_role = 'replica';")
        
        # Truncate all tables
        for table in tables:
            if table != "alembic_version":  # Don't truncate alembic_version
                logger.info(f"Truncating table: {table}")
                cursor.execute(f'TRUNCATE TABLE "{table}" CASCADE;')
        
        # Reset sequences
        cursor.execute("""
            SELECT sequence_name 
            FROM information_schema.sequences 
            WHERE sequence_schema = 'public'
        """)
        
        sequences = [row["sequence_name"] for row in cursor.fetchall()]
        
        for sequence in sequences:
            logger.info(f"Resetting sequence: {sequence}")
            cursor.execute(f'ALTER SEQUENCE "{sequence}" RESTART WITH 1;')
        
        # Re-enable foreign key constraints
        cursor.execute("SET session_replication_role = 'origin';")
        
        logger.info("Database reset completed successfully")
    except Exception as e:
        logger.error(f"Error resetting database: {str(e)}")
        raise
    finally:
        cursor.close()

def create_test_users(conn, num_users=10):
    """
    Create test users in the database.
    
    Args:
        conn: Database connection
        num_users: Number of test users to create
    """
    cursor = conn.cursor()
    
    try:
        # Create admin user
        admin_username = os.getenv("TEST_ADMIN_USERNAME", "testadmin")
        admin_password = os.getenv("TEST_ADMIN_PASSWORD", "testadminpassword")
        admin_email = os.getenv("TEST_ADMIN_EMAIL", "testadmin@example.com")
        
        # Check if admin user already exists
        cursor.execute("SELECT id FROM users WHERE username = %s", (admin_username,))
        if not cursor.fetchone():
            logger.info(f"Creating admin user: {admin_username}")
            
            # In a real environment, you would hash the password
            # For testing, we're using a placeholder
            cursor.execute("""
                INSERT INTO users (
                    username, email, hashed_password, full_name, 
                    is_active, is_superuser, created_at
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                admin_username,
                admin_email,
                f"hashed_{admin_password}",  # Placeholder for hashed password
                "Test Admin",
                True,
                True,
                datetime.now()
            ))
        
        # Create regular test users
        for i in range(1, num_users + 1):
            username = f"testuser{i}"
            email = f"testuser{i}@example.com"
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if not cursor.fetchone():
                logger.info(f"Creating test user: {username}")
                
                cursor.execute("""
                    INSERT INTO users (
                        username, email, hashed_password, full_name, 
                        is_active, is_superuser, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    username,
                    email,
                    f"hashed_testpassword",  # Placeholder for hashed password
                    f"Test User {i}",
                    True,
                    False,
                    datetime.now()
                ))
        
        # Create load test users
        for i in range(1, 6):
            username = f"loadtest{i}"
            email = f"loadtest{i}@example.com"
            
            # Check if user already exists
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if not cursor.fetchone():
                logger.info(f"Creating load test user: {username}")
                
                cursor.execute("""
                    INSERT INTO users (
                        username, email, hashed_password, full_name, 
                        is_active, is_superuser, created_at
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    username,
                    email,
                    f"hashed_testpassword",  # Placeholder for hashed password
                    f"Load Test User {i}",
                    True,
                    False,
                    datetime.now()
                ))
        
        logger.info(f"Created {num_users} test users, 5 load test users, and 1 admin user")
    except Exception as e:
        logger.error(f"Error creating test users: {str(e)}")
        raise
    finally:
        cursor.close()

def create_test_events(conn, num_events=20):
    """
    Create test events in the database.
    
    Args:
        conn: Database connection
        num_events: Number of test events to create
    """
    cursor = conn.cursor()
    
    try:
        # Event types
        event_types = ["workshop", "social", "trivia", "game_night", "networking"]
        
        # Locations
        locations = [
            "Main Hall, Pine Time Center",
            "Conference Room A, Pine Time Center",
            "Conference Room B, Pine Time Center",
            "Outdoor Pavilion, Pine Time Park",
            "Virtual Meeting Room"
        ]
        
        # Create past, current, and future events
        now = datetime.now()
        
        # Past events (30% of total)
        past_count = int(num_events * 0.3)
        for i in range(1, past_count + 1):
            days_ago = random.randint(1, 30)
            hours = random.randint(1, 3)
            
            start_time = now - timedelta(days=days_ago, hours=random.randint(0, 12))
            end_time = start_time + timedelta(hours=hours)
            
            title = f"Past Test Event {i}"
            event_type = random.choice(event_types)
            location = random.choice(locations)
            max_participants = random.randint(10, 50)
            points_reward = random.randint(5, 20)
            
            logger.info(f"Creating past event: {title}")
            
            cursor.execute("""
                INSERT INTO events (
                    title, description, event_type, location,
                    start_time, end_time, max_participants, points_reward
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                title,
                f"This is a past test event for {event_type}",
                event_type,
                location,
                start_time,
                end_time,
                max_participants,
                points_reward
            ))
        
        # Current events (10% of total)
        current_count = int(num_events * 0.1)
        for i in range(1, current_count + 1):
            hours_offset = random.randint(-1, 1)
            hours_duration = random.randint(2, 4)
            
            start_time = now + timedelta(hours=hours_offset)
            end_time = start_time + timedelta(hours=hours_duration)
            
            title = f"Current Test Event {i}"
            event_type = random.choice(event_types)
            location = random.choice(locations)
            max_participants = random.randint(10, 50)
            points_reward = random.randint(5, 20)
            
            logger.info(f"Creating current event: {title}")
            
            cursor.execute("""
                INSERT INTO events (
                    title, description, event_type, location,
                    start_time, end_time, max_participants, points_reward
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                title,
                f"This is a current test event for {event_type}",
                event_type,
                location,
                start_time,
                end_time,
                max_participants,
                points_reward
            ))
        
        # Future events (60% of total)
        future_count = num_events - past_count - current_count
        for i in range(1, future_count + 1):
            days_ahead = random.randint(1, 30)
            hours = random.randint(1, 3)
            
            start_time = now + timedelta(days=days_ahead, hours=random.randint(0, 12))
            end_time = start_time + timedelta(hours=hours)
            
            title = f"Future Test Event {i}"
            event_type = random.choice(event_types)
            location = random.choice(locations)
            max_participants = random.randint(10, 50)
            points_reward = random.randint(5, 20)
            
            logger.info(f"Creating future event: {title}")
            
            cursor.execute("""
                INSERT INTO events (
                    title, description, event_type, location,
                    start_time, end_time, max_participants, points_reward
                ) VALUES (
                    %s, %s, %s, %s, %s, %s, %s, %s
                )
            """, (
                title,
                f"This is a future test event for {event_type}",
                event_type,
                location,
                start_time,
                end_time,
                max_participants,
                points_reward
            ))
        
        logger.info(f"Created {num_events} test events ({past_count} past, {current_count} current, {future_count} future)")
    except Exception as e:
        logger.error(f"Error creating test events: {str(e)}")
        raise
    finally:
        cursor.close()

def create_test_badges(conn):
    """
    Create test badges in the database.
    
    Args:
        conn: Database connection
    """
    cursor = conn.cursor()
    
    try:
        # Badge definitions
        badges = [
            {
                "name": "First Timer",
                "description": "Attended your first event",
                "category": "attendance",
                "level": "bronze",
                "points": 10
            },
            {
                "name": "Trivia Master",
                "description": "Won a trivia night event",
                "category": "achievement",
                "level": "silver",
                "points": 25
            },
            {
                "name": "Social Butterfly",
                "description": "Attended 5 different event types",
                "category": "attendance",
                "level": "bronze",
                "points": 15
            },
            {
                "name": "Event Organizer",
                "description": "Helped organize an event",
                "category": "contribution",
                "level": "gold",
                "points": 50
            },
            {
                "name": "3-Day Streak",
                "description": "Attended events 3 days in a row",
                "category": "streak",
                "level": "bronze",
                "points": 20
            },
            {
                "name": "7-Day Streak",
                "description": "Attended events 7 days in a row",
                "category": "streak",
                "level": "silver",
                "points": 40
            },
            {
                "name": "30-Day Streak",
                "description": "Attended events 30 days in a row",
                "category": "streak",
                "level": "gold",
                "points": 100
            },
            {
                "name": "Community Champion",
                "description": "Reached 1000 points",
                "category": "achievement",
                "level": "gold",
                "points": 75
            }
        ]
        
        # Create badges
        for badge in badges:
            # Check if badge already exists
            cursor.execute("SELECT id FROM badges WHERE name = %s", (badge["name"],))
            if not cursor.fetchone():
                logger.info(f"Creating badge: {badge['name']}")
                
                cursor.execute("""
                    INSERT INTO badges (
                        name, description, category, level, points
                    ) VALUES (
                        %s, %s, %s, %s, %s
                    )
                """, (
                    badge["name"],
                    badge["description"],
                    badge["category"],
                    badge["level"],
                    badge["points"]
                ))
        
        logger.info(f"Created {len(badges)} test badges")
    except Exception as e:
        logger.error(f"Error creating test badges: {str(e)}")
        raise
    finally:
        cursor.close()

def create_test_registrations(conn):
    """
    Create test event registrations in the database.
    
    Args:
        conn: Database connection
    """
    cursor = conn.cursor()
    
    try:
        # Get users
        cursor.execute("SELECT id FROM users WHERE is_superuser = FALSE")
        users = [row["id"] for row in cursor.fetchall()]
        
        if not users:
            logger.warning("No users found for registrations")
            return
        
        # Get past events
        cursor.execute("SELECT id FROM events WHERE start_time < NOW()")
        past_events = [row["id"] for row in cursor.fetchall()]
        
        # Get future events
        cursor.execute("SELECT id FROM events WHERE start_time > NOW()")
        future_events = [row["id"] for row in cursor.fetchall()]
        
        # Create registrations for past events (with check-ins)
        for event_id in past_events:
            # Register random users (30-70% of users)
            num_registrations = random.randint(int(len(users) * 0.3), int(len(users) * 0.7))
            registered_users = random.sample(users, num_registrations)
            
            for user_id in registered_users:
                # Check if registration already exists
                cursor.execute(
                    "SELECT id FROM registrations WHERE event_id = %s AND user_id = %s",
                    (event_id, user_id)
                )
                if not cursor.fetchone():
                    logger.info(f"Creating past event registration: Event {event_id}, User {user_id}")
                    
                    # Create registration
                    cursor.execute("""
                        INSERT INTO registrations (
                            event_id, user_id, registration_date, status
                        ) VALUES (
                            %s, %s, %s, %s
                        )
                    """, (
                        event_id,
                        user_id,
                        datetime.now() - timedelta(days=random.randint(1, 14)),
                        "attended"  # Past events are marked as attended
                    ))
                    
                    # Add points for attendance
                    cursor.execute("SELECT points_reward FROM events WHERE id = %s", (event_id,))
                    event_result = cursor.fetchone()
                    points_reward = event_result["points_reward"] if event_result else 10
                    
                    cursor.execute("""
                        INSERT INTO points_transactions (
                            user_id, points, transaction_type, description, created_at
                        ) VALUES (
                            %s, %s, %s, %s, %s
                        )
                    """, (
                        user_id,
                        points_reward,
                        "event_attendance",
                        f"Attended event {event_id}",
                        datetime.now() - timedelta(days=random.randint(0, 7))
                    ))
        
        # Create registrations for future events
        for event_id in future_events:
            # Register random users (10-40% of users)
            num_registrations = random.randint(int(len(users) * 0.1), int(len(users) * 0.4))
            registered_users = random.sample(users, num_registrations)
            
            for user_id in registered_users:
                # Check if registration already exists
                cursor.execute(
                    "SELECT id FROM registrations WHERE event_id = %s AND user_id = %s",
                    (event_id, user_id)
                )
                if not cursor.fetchone():
                    logger.info(f"Creating future event registration: Event {event_id}, User {user_id}")
                    
                    # Create registration
                    cursor.execute("""
                        INSERT INTO registrations (
                            event_id, user_id, registration_date, status
                        ) VALUES (
                            %s, %s, %s, %s
                        )
                    """, (
                        event_id,
                        user_id,
                        datetime.now() - timedelta(days=random.randint(0, 7)),
                        "registered"  # Future events are marked as registered
                    ))
        
        logger.info("Created test registrations for past and future events")
    except Exception as e:
        logger.error(f"Error creating test registrations: {str(e)}")
        raise
    finally:
        cursor.close()

def award_test_badges(conn):
    """
    Award test badges to users in the database.
    
    Args:
        conn: Database connection
    """
    cursor = conn.cursor()
    
    try:
        # Get users
        cursor.execute("SELECT id FROM users WHERE is_superuser = FALSE")
        users = [row["id"] for row in cursor.fetchall()]
        
        if not users:
            logger.warning("No users found for badge awards")
            return
        
        # Get badges
        cursor.execute("SELECT id, name, points FROM badges")
        badges = cursor.fetchall()
        
        if not badges:
            logger.warning("No badges found for awards")
            return
        
        # Award badges to random users
        for badge in badges:
            # Award to 20-50% of users
            num_awards = random.randint(int(len(users) * 0.2), int(len(users) * 0.5))
            awarded_users = random.sample(users, num_awards)
            
            for user_id in awarded_users:
                # Check if user already has this badge
                cursor.execute(
                    "SELECT id FROM user_badges WHERE badge_id = %s AND user_id = %s",
                    (badge["id"], user_id)
                )
                if not cursor.fetchone():
                    logger.info(f"Awarding badge: {badge['name']} to User {user_id}")
                    
                    # Award badge
                    cursor.execute("""
                        INSERT INTO user_badges (
                            user_id, badge_id, awarded_at
                        ) VALUES (
                            %s, %s, %s
                        )
                    """, (
                        user_id,
                        badge["id"],
                        datetime.now() - timedelta(days=random.randint(0, 30))
                    ))
                    
                    # Add points for badge
                    cursor.execute("""
                        INSERT INTO points_transactions (
                            user_id, points, transaction_type, description, created_at
                        ) VALUES (
                            %s, %s, %s, %s, %s
                        )
                    """, (
                        user_id,
                        badge["points"],
                        "badge_earned",
                        f"Earned badge: {badge['name']}",
                        datetime.now() - timedelta(days=random.randint(0, 30))
                    ))
        
        logger.info("Awarded test badges to users")
    except Exception as e:
        logger.error(f"Error awarding test badges: {str(e)}")
        raise
    finally:
        cursor.close()

def verify_api_connection():
    """
    Verify API connection and endpoints.
    
    Returns:
        bool: True if API is working, False otherwise
    """
    api_base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    api_v1_str = "/api/v1"
    
    # Endpoints to check
    endpoints = [
        "/health",  # Health check endpoint
        "/docs",    # Swagger docs
        "/openapi.json"  # OpenAPI schema
    ]
    
    success = True
    
    for endpoint in endpoints:
        url = f"{api_base_url}{endpoint}"
        try:
            logger.info(f"Checking endpoint: {url}")
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                logger.info(f"Endpoint {url} is available")
            else:
                logger.warning(f"Endpoint {url} returned status code {response.status_code}")
                success = False
        except Exception as e:
            logger.error(f"Error connecting to {url}: {str(e)}")
            success = False
    
    # Try to login with test admin
    admin_username = os.getenv("TEST_ADMIN_USERNAME", "testadmin")
    admin_password = os.getenv("TEST_ADMIN_PASSWORD", "testadminpassword")
    
    try:
        logger.info(f"Attempting to login as {admin_username}")
        login_url = f"{api_base_url}{api_v1_str}/login/access-token"
        
        response = requests.post(
            login_url,
            data={"username": admin_username, "password": admin_password},
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=5
        )
        
        if response.status_code == 200:
            result = response.json()
            if "access_token" in result:
                logger.info(f"Successfully logged in as {admin_username}")
                
                # Try to get user profile
                token = result["access_token"]
                profile_url = f"{api_base_url}{api_v1_str}/users/me"
                
                profile_response = requests.get(
                    profile_url,
                    headers={"Authorization": f"Bearer {token}"},
                    timeout=5
                )
                
                if profile_response.status_code == 200:
                    logger.info("Successfully retrieved user profile")
                else:
                    logger.warning(f"Failed to get user profile: {profile_response.status_code}")
                    success = False
            else:
                logger.warning("Login response did not contain access_token")
                success = False
        else:
            logger.warning(f"Failed to login: {response.status_code}")
            success = False
    except Exception as e:
        logger.error(f"Error during login test: {str(e)}")
        success = False
    
    return success

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Set up test environment for Pine Time App")
    
    parser.add_argument("--reset-db", action="store_true", help="Reset database (truncate tables)")
    parser.add_argument("--create-test-users", action="store_true", help="Create test users")
    parser.add_argument("--create-test-data", action="store_true", help="Create test data (events, badges, etc.)")
    parser.add_argument("--verify-api", action="store_true", help="Verify API connection")
    parser.add_argument("--all", action="store_true", help="Perform all setup steps")
    
    args = parser.parse_args()
    
    # If no arguments provided, show help
    if not any(vars(args).values()):
        parser.print_help()
        return 1
    
    try:
        # Connect to database
        conn = get_postgres_connection()
        
        # Reset database if requested
        if args.reset_db or args.all:
            logger.info("Resetting database...")
            reset_database(conn)
        
        # Create test users if requested
        if args.create_test_users or args.all:
            logger.info("Creating test users...")
            create_test_users(conn)
        
        # Create test data if requested
        if args.create_test_data or args.all:
            logger.info("Creating test events...")
            create_test_events(conn)
            
            logger.info("Creating test badges...")
            create_test_badges(conn)
            
            logger.info("Creating test registrations...")
            create_test_registrations(conn)
            
            logger.info("Awarding test badges...")
            award_test_badges(conn)
        
        # Verify API connection if requested
        if args.verify_api or args.all:
            logger.info("Verifying API connection...")
            if verify_api_connection():
                logger.info("API verification successful")
            else:
                logger.warning("API verification failed")
        
        # Close database connection
        conn.close()
        
        logger.info("Test environment setup completed")
        return 0
    
    except Exception as e:
        logger.error(f"Error setting up test environment: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())