"""
Pine Time Application - Database Load Testing Script
Tests the PostgreSQL database connection and performance under load.
Follows project guidelines for proper PostgreSQL integration and error handling.
"""

import os
import sys
import time
import random
import logging
import psycopg2
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timedelta
from locust import User, task, between, events
from locust.env import Environment
from dotenv import load_dotenv

# Add project root to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("db_load_test.log")
    ]
)
logger = logging.getLogger("db_load_test")

# Load environment variables
load_dotenv()

# Database configuration
DB_CONFIG = {
    "host": os.getenv("POSTGRES_SERVER", "localhost"),
    "port": int(os.getenv("POSTGRES_PORT", "5432")),
    "database": os.getenv("POSTGRES_DB", "pine_time"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "pool_size": int(os.getenv("POOL_SIZE", "5")),
    "pool_pre_ping": os.getenv("POOL_PRE_PING", "True").lower() == "true",
    "connect_timeout": int(os.getenv("DB_CONNECT_TIMEOUT", "5"))
}

# Test configuration
CONFIG = {
    "users": {
        "min_wait": int(os.getenv("LOAD_TEST_MIN_WAIT", "1")),
        "max_wait": int(os.getenv("LOAD_TEST_MAX_WAIT", "5")),
        "count": int(os.getenv("LOAD_TEST_USER_COUNT", "10")),
        "spawn_rate": int(os.getenv("LOAD_TEST_SPAWN_RATE", "2")),
    },
    "retry": {
        "attempts": int(os.getenv("DB_RETRY_ATTEMPTS", "3")),
        "delay": int(os.getenv("DB_RETRY_DELAY", "2")),
    }
}

class PostgreSQLError(Exception):
    """Custom exception for PostgreSQL errors"""
    def __init__(self, message, pg_code=None):
        self.message = message
        self.pg_code = pg_code
        super().__init__(self.message)

def get_connection():
    """
    Get a PostgreSQL connection with retry logic.
    
    Returns:
        psycopg2.connection: PostgreSQL connection
    
    Raises:
        PostgreSQLError: If connection fails after all retries
    """
    retry_count = 0
    max_retries = CONFIG["retry"]["attempts"]
    retry_delay = CONFIG["retry"]["delay"]
    
    while retry_count < max_retries:
        try:
            conn = psycopg2.connect(
                host=DB_CONFIG["host"],
                port=DB_CONFIG["port"],
                database=DB_CONFIG["database"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                connect_timeout=DB_CONFIG["connect_timeout"]
            )
            return conn
        except psycopg2.Error as e:
            retry_count += 1
            if retry_count < max_retries:
                logger.warning(f"Database connection attempt {retry_count} failed: {e}")
                time.sleep(retry_delay * (2 ** (retry_count - 1)))  # Exponential backoff
            else:
                logger.error(f"Database connection failed after {max_retries} attempts: {e}")
                raise PostgreSQLError(f"Database connection failed: {e}", e.pgcode if hasattr(e, 'pgcode') else None)
        except Exception as e:
            logger.error(f"Unexpected error connecting to database: {e}")
            raise PostgreSQLError(f"Unexpected error connecting to database: {e}")

class DatabaseUser(User):
    """
    Simulated user for load testing the PostgreSQL database.
    """
    
    wait_time = between(CONFIG["users"]["min_wait"], CONFIG["users"]["max_wait"])
    abstract = True
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.conn = None
    
    def on_start(self):
        """
        Called when a user starts.
        Establish database connection.
        """
        logger.info("Starting database user simulation")
        self.connect_to_database()
    
    def connect_to_database(self):
        """
        Connect to the PostgreSQL database with retry logic.
        """
        try:
            start_time = time.time()
            self.conn = get_connection()
            response_time = int((time.time() - start_time) * 1000)
            
            self.environment.events.request.fire(
                request_type="DB",
                name="Connect",
                response_time=response_time,
                response_length=0,
                exception=None,
                context={}
            )
            
            logger.info("Connected to database successfully")
            return True
        except PostgreSQLError as e:
            response_time = int((time.time() - start_time) * 1000)
            
            self.environment.events.request.fire(
                request_type="DB",
                name="Connect",
                response_time=response_time,
                response_length=0,
                exception=e,
                context={}
            )
            
            logger.error(f"Failed to connect to database: {e}")
            return False
    
    def execute_query(self, query_name, query, params=None):
        """
        Execute a database query with proper error handling.
        
        Args:
            query_name: Name of the query for logging
            query: SQL query to execute
            params: Query parameters
            
        Returns:
            Tuple[bool, List]: Success flag and query results
        """
        if not self.conn:
            if not self.connect_to_database():
                return False, []
        
        try:
            start_time = time.time()
            cursor = self.conn.cursor()
            cursor.execute(query, params or ())
            results = cursor.fetchall()
            self.conn.commit()
            cursor.close()
            
            response_time = int((time.time() - start_time) * 1000)
            
            self.environment.events.request.fire(
                request_type="DB",
                name=query_name,
                response_time=response_time,
                response_length=len(results),
                exception=None,
                context={}
            )
            
            return True, results
        except psycopg2.Error as e:
            response_time = int((time.time() - start_time) * 1000)
            
            self.environment.events.request.fire(
                request_type="DB",
                name=query_name,
                response_time=response_time,
                response_length=0,
                exception=e,
                context={}
            )
            
            logger.error(f"Database query '{query_name}' failed: {e}")
            
            # Try to reconnect if connection is closed
            if "connection is closed" in str(e) or "connection already closed" in str(e):
                logger.info("Reconnecting to database...")
                self.conn = None
                self.connect_to_database()
            
            return False, []
    
    def on_stop(self):
        """
        Called when a user stops.
        Close database connection.
        """
        if self.conn:
            try:
                self.conn.close()
                logger.info("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {e}")

class EventQueryUser(DatabaseUser):
    """
    User that performs event-related database queries.
    """
    
    @task(5)
    def query_events(self):
        """
        Query events from the database.
        Higher weight (5) as this is a common operation.
        """
        success, results = self.execute_query(
            "Query Events",
            "SELECT id, name, description, location, start_time, end_time, max_capacity, points FROM events ORDER BY start_time DESC LIMIT 100"
        )
        
        if success:
            logger.info(f"Retrieved {len(results)} events")
    
    @task(3)
    def query_upcoming_events(self):
        """
        Query upcoming events from the database.
        Medium weight (3) as this is checked regularly.
        """
        success, results = self.execute_query(
            "Query Upcoming Events",
            "SELECT id, name, description, location, start_time, end_time, max_capacity, points FROM events WHERE start_time > NOW() ORDER BY start_time ASC LIMIT 50"
        )
        
        if success:
            logger.info(f"Retrieved {len(results)} upcoming events")
    
    @task(2)
    def query_event_registrations(self):
        """
        Query event registrations from the database.
        Lower weight (2) as this is checked less frequently.
        """
        success, results = self.execute_query(
            "Query Event Registrations",
            "SELECT e.name, COUNT(r.id) as registrations FROM events e LEFT JOIN registrations r ON e.id = r.event_id GROUP BY e.id, e.name ORDER BY registrations DESC LIMIT 20"
        )
        
        if success:
            logger.info(f"Retrieved registration counts for {len(results)} events")
    
    @task(1)
    def query_event_by_id(self):
        """
        Query a specific event by ID.
        Lowest weight (1) as this is done infrequently.
        """
        # Generate a random ID between 1 and 100
        event_id = random.randint(1, 100)
        
        success, results = self.execute_query(
            "Query Event by ID",
            "SELECT id, name, description, location, start_time, end_time, max_capacity, points FROM events WHERE id = %s",
            (event_id,)
        )
        
        if success:
            if results:
                logger.info(f"Retrieved event with ID {event_id}")
            else:
                logger.info(f"No event found with ID {event_id}")

class UserQueryUser(DatabaseUser):
    """
    User that performs user-related database queries.
    """
    
    @task(3)
    def query_users(self):
        """
        Query users from the database.
        Medium weight (3) as this is a common admin operation.
        """
        success, results = self.execute_query(
            "Query Users",
            "SELECT id, username, email, full_name, is_active, is_admin FROM users LIMIT 100"
        )
        
        if success:
            logger.info(f"Retrieved {len(results)} users")
    
    @task(2)
    def query_user_points(self):
        """
        Query user points from the database.
        Lower weight (2) as this is checked less frequently.
        """
        success, results = self.execute_query(
            "Query User Points",
            "SELECT u.username, COALESCE(SUM(p.points), 0) as total_points FROM users u LEFT JOIN points p ON u.id = p.user_id GROUP BY u.id, u.username ORDER BY total_points DESC LIMIT 20"
        )
        
        if success:
            logger.info(f"Retrieved points for {len(results)} users")
    
    @task(2)
    def query_user_badges(self):
        """
        Query user badges from the database.
        Lower weight (2) as this is checked less frequently.
        """
        success, results = self.execute_query(
            "Query User Badges",
            "SELECT u.username, COUNT(ub.badge_id) as badge_count FROM users u LEFT JOIN user_badges ub ON u.id = ub.user_id GROUP BY u.id, u.username ORDER BY badge_count DESC LIMIT 20"
        )
        
        if success:
            logger.info(f"Retrieved badge counts for {len(results)} users")
    
    @task(1)
    def query_user_by_id(self):
        """
        Query a specific user by ID.
        Lowest weight (1) as this is done infrequently.
        """
        # Generate a random ID between 1 and 100
        user_id = random.randint(1, 100)
        
        success, results = self.execute_query(
            "Query User by ID",
            "SELECT id, username, email, full_name, is_active, is_admin FROM users WHERE id = %s",
            (user_id,)
        )
        
        if success:
            if results:
                logger.info(f"Retrieved user with ID {user_id}")
            else:
                logger.info(f"No user found with ID {user_id}")

class AnalyticsQueryUser(DatabaseUser):
    """
    User that performs analytics-related database queries.
    """
    
    @task(2)
    def query_event_popularity(self):
        """
        Query event popularity analytics.
        Medium weight (2) as this is checked regularly by admins.
        """
        success, results = self.execute_query(
            "Query Event Popularity",
            """
            SELECT e.name, COUNT(r.id) as registration_count
            FROM events e
            LEFT JOIN registrations r ON e.id = r.event_id
            GROUP BY e.id, e.name
            ORDER BY registration_count DESC
            LIMIT 10
            """
        )
        
        if success:
            logger.info(f"Retrieved popularity data for {len(results)} events")
    
    @task(2)
    def query_user_engagement(self):
        """
        Query user engagement analytics.
        Medium weight (2) as this is checked regularly by admins.
        """
        success, results = self.execute_query(
            "Query User Engagement",
            """
            SELECT u.username, COUNT(r.id) as event_count
            FROM users u
            LEFT JOIN registrations r ON u.id = r.user_id
            GROUP BY u.id, u.username
            ORDER BY event_count DESC
            LIMIT 10
            """
        )
        
        if success:
            logger.info(f"Retrieved engagement data for {len(results)} users")
    
    @task(1)
    def query_points_distribution(self):
        """
        Query points distribution analytics.
        Lowest weight (1) as this is checked less frequently.
        """
        success, results = self.execute_query(
            "Query Points Distribution",
            """
            SELECT 
                CASE 
                    WHEN total_points BETWEEN 0 AND 100 THEN '0-100'
                    WHEN total_points BETWEEN 101 AND 500 THEN '101-500'
                    WHEN total_points BETWEEN 501 AND 1000 THEN '501-1000'
                    ELSE '1000+'
                END as point_range,
                COUNT(user_id) as user_count
            FROM (
                SELECT user_id, COALESCE(SUM(points), 0) as total_points
                FROM points
                GROUP BY user_id
            ) as user_points
            GROUP BY point_range
            ORDER BY point_range
            """
        )
        
        if success:
            logger.info(f"Retrieved points distribution data with {len(results)} ranges")

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    """
    Called when Locust is initialized.
    """
    logger.info("Locust initialized")
    logger.info(f"Database configuration: {DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}")
    logger.info(f"User configuration: {CONFIG['users']}")
    logger.info(f"Retry configuration: {CONFIG['retry']}")

@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Called when the test is started.
    """
    logger.info("Load test starting")
    
    # Test database connection
    try:
        conn = get_connection()
        logger.info("Database connection test successful")
        conn.close()
    except PostgreSQLError as e:
        logger.error(f"Database connection test failed: {e}")

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Called when the test is stopped.
    """
    logger.info("Load test complete")
    
    # Calculate statistics
    stats = environment.stats
    
    # Total requests
    total_requests = stats.total.num_requests
    # Success rate
    success_rate = 0 if total_requests == 0 else (total_requests - stats.total.num_failures) / total_requests * 100
    # Average response time
    avg_response_time = stats.total.avg_response_time
    
    logger.info(f"Total database queries: {total_requests}")
    logger.info(f"Success rate: {success_rate:.2f}%")
    logger.info(f"Average response time: {avg_response_time:.2f} ms")
    
    # Log detailed stats for each query
    logger.info("Query statistics:")
    for name, stat in stats.entries.items():
        logger.info(f"  {name}:")
        logger.info(f"    Queries: {stat.num_requests}")
        logger.info(f"    Failures: {stat.num_failures}")
        logger.info(f"    Median response time: {stat.median_response_time} ms")
        logger.info(f"    95th percentile: {stat.get_response_time_percentile(0.95)} ms")

if __name__ == "__main__":
    # This script is meant to be run with the Locust command-line interface
    logger.info("Database load test script loaded")
