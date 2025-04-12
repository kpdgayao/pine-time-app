"""
Test script for PostgreSQL integration in Pine Time App.
Tests the database connection and error handling mechanisms.
"""

import os
import sys
import unittest
import logging
from typing import Dict, Any, Optional
import psycopg2
from psycopg2.extras import RealDictCursor

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("test_postgres_integration.log")
    ]
)
logger = logging.getLogger("test_postgres_integration")

class TestPostgresIntegration(unittest.TestCase):
    """Test PostgreSQL integration."""
    
    def setUp(self):
        """Set up test environment."""
        # Get database connection parameters from environment variables
        self.db_params = {
            "host": os.getenv("POSTGRES_SERVER", "localhost"),
            "port": os.getenv("POSTGRES_PORT", "5432"),
            "user": os.getenv("POSTGRES_USER", "postgres"),
            "password": os.getenv("POSTGRES_PASSWORD", ""),
            "dbname": os.getenv("POSTGRES_DB", "pine_time"),
            "cursor_factory": RealDictCursor
        }
        
        # Connect to database
        try:
            self.conn = psycopg2.connect(**self.db_params)
            self.conn.set_session(autocommit=False)  # Use transactions for tests
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    def tearDown(self):
        """Tear down test environment."""
        # Rollback any changes and close connection
        if hasattr(self, "conn"):
            self.conn.rollback()
            self.conn.close()
    
    def test_database_connection(self):
        """Test database connection."""
        # Execute a simple query
        cursor = self.conn.cursor()
        cursor.execute("SELECT 1 AS test")
        result = cursor.fetchone()
        cursor.close()
        
        # Check result
        self.assertIsNotNone(result)
        self.assertEqual(result["test"], 1)
    
    def test_table_structure(self):
        """Test that required tables exist."""
        # Get list of tables
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' AND table_type = 'BASE TABLE'
        """)
        tables = [row["table_name"] for row in cursor.fetchall()]
        cursor.close()
        
        # Check that required tables exist
        required_tables = ["users", "events", "registrations", "badges", "user_badges", "points_transactions"]
        for table in required_tables:
            self.assertIn(table, tables, f"Table {table} not found in database")
    
    def test_user_table_structure(self):
        """Test user table structure."""
        # Get columns in users table
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'users'
        """)
        columns = {row["column_name"]: row for row in cursor.fetchall()}
        cursor.close()
        
        # Check required columns
        required_columns = ["id", "username", "email", "hashed_password", "full_name", "is_active", "is_superuser", "created_at"]
        for column in required_columns:
            self.assertIn(column, columns, f"Column {column} not found in users table")
        
        # Check id column is not nullable
        self.assertEqual(columns["id"]["is_nullable"], "NO", "id column should not be nullable")
        
        # Check unique constraints
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT tc.constraint_name, tc.constraint_type, kcu.column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
            WHERE tc.table_name = 'users'
              AND tc.constraint_type = 'UNIQUE'
        """)
        unique_constraints = cursor.fetchall()
        cursor.close()
        
        # Check that username and email have unique constraints
        unique_columns = [row["column_name"] for row in unique_constraints]
        self.assertIn("username", unique_columns, "username column should have a unique constraint")
        self.assertIn("email", unique_columns, "email column should have a unique constraint")
    
    def test_event_table_structure(self):
        """Test event table structure."""
        # Get columns in events table
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'events'
        """)
        columns = {row["column_name"]: row for row in cursor.fetchall()}
        cursor.close()
        
        # Check required columns
        required_columns = ["id", "title", "description", "event_type", "location", "start_time", "end_time", "max_participants", "points_reward"]
        for column in required_columns:
            self.assertIn(column, columns, f"Column {column} not found in events table")
        
        # Check id column is not nullable
        self.assertEqual(columns["id"]["is_nullable"], "NO", "id column should not be nullable")
        
        # Check date columns have correct data type
        self.assertTrue(columns["start_time"]["data_type"].startswith("timestamp"), "start_time should be a timestamp")
        self.assertTrue(columns["end_time"]["data_type"].startswith("timestamp"), "end_time should be a timestamp")
    
    def test_registration_table_structure(self):
        """Test registration table structure."""
        # Get columns in registrations table
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'registrations'
        """)
        columns = {row["column_name"]: row for row in cursor.fetchall()}
        cursor.close()
        
        # Check required columns
        required_columns = ["id", "user_id", "event_id", "registration_date", "status"]
        for column in required_columns:
            self.assertIn(column, columns, f"Column {column} not found in registrations table")
        
        # Check foreign key columns are not nullable
        self.assertEqual(columns["user_id"]["is_nullable"], "NO", "user_id column should not be nullable")
        self.assertEqual(columns["event_id"]["is_nullable"], "NO", "event_id column should not be nullable")
        
        # Check foreign key constraints
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT tc.constraint_name, tc.constraint_type, kcu.column_name,
                   ccu.table_name AS foreign_table_name,
                   ccu.column_name AS foreign_column_name
            FROM information_schema.table_constraints tc
            JOIN information_schema.key_column_usage kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage ccu
              ON tc.constraint_name = ccu.constraint_name
            WHERE tc.table_name = 'registrations'
              AND tc.constraint_type = 'FOREIGN KEY'
        """)
        foreign_keys = cursor.fetchall()
        cursor.close()
        
        # Check foreign key constraints
        foreign_key_columns = {row["column_name"]: row for row in foreign_keys}
        self.assertIn("user_id", foreign_key_columns, "user_id should have a foreign key constraint")
        self.assertIn("event_id", foreign_key_columns, "event_id should have a foreign key constraint")
        self.assertEqual(foreign_key_columns["user_id"]["foreign_table_name"], "users", "user_id should reference users table")
        self.assertEqual(foreign_key_columns["event_id"]["foreign_table_name"], "events", "event_id should reference events table")
    
    def test_null_constraint_handling(self):
        """Test handling of NULL constraints in the database."""
        # Try to insert a record with NULL user_id into registrations
        cursor = self.conn.cursor()
        
        # First, get a valid event_id
        cursor.execute("SELECT id FROM events LIMIT 1")
        event_result = cursor.fetchone()
        
        if not event_result:
            self.skipTest("No events found in database")
        
        event_id = event_result["id"]
        
        # Try to insert with NULL user_id
        with self.assertRaises(Exception) as context:
            cursor.execute("""
                INSERT INTO registrations (user_id, event_id, registration_date, status)
                VALUES (NULL, %s, NOW(), 'registered')
            """, (event_id,))
            self.conn.commit()
        
        # Check that the exception is related to NOT NULL constraint
        self.assertTrue(
            "null" in str(context.exception).lower() or 
            "not null" in str(context.exception).lower(),
            "Exception should mention NULL constraint violation"
        )
        
        # Rollback the transaction
        self.conn.rollback()
    
    def test_unique_constraint_handling(self):
        """Test handling of unique constraints in the database."""
        # Try to insert a duplicate username
        cursor = self.conn.cursor()
        
        # First, insert a test user
        test_username = f"test_unique_{os.urandom(4).hex()}"
        test_email = f"{test_username}@example.com"
        
        cursor.execute("""
            INSERT INTO users (username, email, hashed_password, full_name, is_active, is_superuser, created_at)
            VALUES (%s, %s, %s, %s, %s, %s, NOW())
        """, (
            test_username,
            test_email,
            "hashed_test_password",
            "Test User",
            True,
            False
        ))
        
        # Try to insert another user with the same username
        with self.assertRaises(Exception) as context:
            cursor.execute("""
                INSERT INTO users (username, email, hashed_password, full_name, is_active, is_superuser, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, NOW())
            """, (
                test_username,
                f"different_{test_email}",
                "hashed_test_password",
                "Test User 2",
                True,
                False
            ))
        
        # Check that the exception is related to unique constraint
        self.assertTrue(
            "unique" in str(context.exception).lower() or 
            "duplicate" in str(context.exception).lower(),
            "Exception should mention unique constraint violation"
        )
        
        # Rollback the transaction
        self.conn.rollback()
    
    def test_foreign_key_constraint_handling(self):
        """Test handling of foreign key constraints in the database."""
        # Try to insert a registration with non-existent user_id
        cursor = self.conn.cursor()
        
        # First, get a valid event_id
        cursor.execute("SELECT id FROM events LIMIT 1")
        event_result = cursor.fetchone()
        
        if not event_result:
            self.skipTest("No events found in database")
        
        event_id = event_result["id"]
        
        # Generate a non-existent user_id
        non_existent_user_id = 999999
        
        # Try to insert with non-existent user_id
        with self.assertRaises(Exception) as context:
            cursor.execute("""
                INSERT INTO registrations (user_id, event_id, registration_date, status)
                VALUES (%s, %s, NOW(), 'registered')
            """, (non_existent_user_id, event_id))
            self.conn.commit()
        
        # Check that the exception is related to foreign key constraint
        self.assertTrue(
            "foreign key" in str(context.exception).lower() or 
            "violates foreign key" in str(context.exception).lower() or
            "referenced" in str(context.exception).lower(),
            "Exception should mention foreign key constraint violation"
        )
        
        # Rollback the transaction
        self.conn.rollback()

if __name__ == "__main__":
    unittest.main()