"""
Database utilities for the Pine Time User Interface.
Handles database connection management and configuration.
"""

import os
import logging
from dotenv import load_dotenv
from typing import Dict, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("db_utils")

# Load environment variables
load_dotenv()

def get_database_config() -> Dict[str, Any]:
    """
    Get database configuration from environment variables.
    
    Returns:
        dict: Database configuration
    """
    database_type = os.getenv("DATABASE_TYPE", "sqlite").lower()
    
    if database_type == "postgresql":
        return {
            "database_type": "postgresql",
            "server": os.getenv("POSTGRES_SERVER"),
            "user": os.getenv("POSTGRES_USER"),
            "password": os.getenv("POSTGRES_PASSWORD"),
            "db": os.getenv("POSTGRES_DB"),
            "port": os.getenv("POSTGRES_PORT", "5432"),
            "ssl_mode": os.getenv("POSTGRES_SSL_MODE", "require"),
            "pool_size": int(os.getenv("POOL_SIZE", "5")),
            "max_overflow": int(os.getenv("MAX_OVERFLOW", "10")),
            "pool_timeout": int(os.getenv("POOL_TIMEOUT", "30")),
            "pool_recycle": int(os.getenv("POOL_RECYCLE", "1800")),
        }
    else:
        return {
            "database_type": "sqlite",
            "uri": os.getenv("SQLITE_DATABASE_URI", "sqlite:///./pine_time.db")
        }

def get_database_uri() -> str:
    """
    Get database URI based on configuration.
    
    Returns:
        str: Database URI
    """
    config = get_database_config()
    
    if config["database_type"] == "postgresql":
        return f"postgresql://{config['user']}:{config['password']}@{config['server']}:{config['port']}/{config['db']}"
    else:
        return config["uri"]

def get_postgres_connection_params() -> Dict[str, Any]:
    """
    Get PostgreSQL connection parameters from environment variables.
    
    Returns:
        Dict[str, Any]: Dictionary with connection parameters
    """
    return {
        "host": os.getenv("POSTGRES_SERVER", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", ""),
        "database": os.getenv("POSTGRES_DB", "postgres"),
        "sslmode": os.getenv("POSTGRES_SSL_MODE", "prefer")
    }

def test_database_connection() -> Optional[str]:
    """
    Test connection to the database.
    
    Returns:
        Optional[str]: Database version if connection successful, None otherwise
    """
    try:
        # Get database configuration
        db_config = get_database_config()
        database_type = db_config.get("database_type", "sqlite").lower()
        
        # Connect to the appropriate database
        if database_type == "postgres" or database_type == "postgresql":
            # Get PostgreSQL connection parameters
            params = get_postgres_connection_params()
            
            # Connect to PostgreSQL
            import psycopg2
            conn = psycopg2.connect(**params)
            
            # Get database version
            cursor = conn.cursor()
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            
            # Close connection
            cursor.close()
            conn.close()
            
            logger.info(f"Successfully connected to PostgreSQL database: {version}")
            return version
            
        elif database_type == "sqlite":
            # Get SQLite database URI
            sqlite_uri = db_config.get("uri", "sqlite:///./pine_time.db")
            
            # Extract file path from URI
            import sqlite3
            from urllib.parse import urlparse
            
            # Parse the URI
            parsed = urlparse(sqlite_uri)
            db_path = parsed.path.lstrip("/")
            
            # Connect to SQLite
            conn = sqlite3.connect(db_path)
            
            # Get database version
            cursor = conn.cursor()
            cursor.execute("SELECT sqlite_version();")
            version = cursor.fetchone()[0]
            
            # Close connection
            cursor.close()
            conn.close()
            
            logger.info(f"Successfully connected to SQLite database: {version}")
            return version
        
        else:
            logger.error(f"Unsupported database type: {database_type}")
            return None
            
    except Exception as e:
        logger.error(f"Database connection error: {str(e)}")
        return None

def create_user_in_database(user_data: Dict[str, Any]) -> bool:
    """
    Create a new user in the database directly (for demo mode).
    
    Args:
        user_data: User registration data
        
    Returns:
        bool: True if user created successfully, False otherwise
    """
    try:
        # Get database configuration
        db_config = get_database_config()
        database_type = db_config.get("database_type", "sqlite").lower()
        
        # Connect to the appropriate database
        if database_type == "postgres" or database_type == "postgresql":
            # Get PostgreSQL connection parameters
            params = get_postgres_connection_params()
            
            # Connect to PostgreSQL
            import psycopg2
            conn = psycopg2.connect(**params)
            
            # Create a cursor
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute(
                "SELECT id FROM users WHERE email = %s OR username = %s",
                (user_data.get("email"), user_data.get("username"))
            )
            
            if cursor.fetchone():
                logger.warning(f"User with email {user_data.get('email')} or username {user_data.get('username')} already exists")
                cursor.close()
                conn.close()
                return False
            
            # Insert new user
            cursor.execute(
                """
                INSERT INTO users (
                    username, email, hashed_password, full_name, is_active, is_superuser, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
                """,
                (
                    user_data.get("username"),
                    user_data.get("email"),
                    # In demo mode, we just store the password directly (not secure, but it's demo)
                    # In production, this would be properly hashed
                    f"demo_hashed_{user_data.get('password')}",
                    user_data.get("full_name"),
                    True,
                    False,
                    datetime.now().isoformat()
                )
            )
            
            # Get the new user ID
            user_id = cursor.fetchone()[0]
            
            # Commit the transaction
            conn.commit()
            
            # Close connection
            cursor.close()
            conn.close()
            
            logger.info(f"Created new user in PostgreSQL database: {user_id}")
            return True
            
        elif database_type == "sqlite":
            # Get SQLite database URI
            sqlite_uri = db_config.get("uri", "sqlite:///./pine_time.db")
            
            # Extract file path from URI
            import sqlite3
            from urllib.parse import urlparse
            
            # Parse the URI
            parsed = urlparse(sqlite_uri)
            db_path = parsed.path.lstrip("/")
            
            # Connect to SQLite
            conn = sqlite3.connect(db_path)
            
            # Create a cursor
            cursor = conn.cursor()
            
            # Check if user already exists
            cursor.execute(
                "SELECT id FROM users WHERE email = ? OR username = ?",
                (user_data.get("email"), user_data.get("username"))
            )
            
            if cursor.fetchone():
                logger.warning(f"User with email {user_data.get('email')} or username {user_data.get('username')} already exists")
                cursor.close()
                conn.close()
                return False
            
            # Insert new user
            cursor.execute(
                """
                INSERT INTO users (
                    username, email, hashed_password, full_name, is_active, is_superuser, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    user_data.get("username"),
                    user_data.get("email"),
                    # In demo mode, we just store the password directly (not secure, but it's demo)
                    f"demo_hashed_{user_data.get('password')}",
                    user_data.get("full_name"),
                    1,
                    0,
                    datetime.now().isoformat()
                )
            )
            
            # Commit the transaction
            conn.commit()
            
            # Close connection
            cursor.close()
            conn.close()
            
            logger.info(f"Created new user in SQLite database")
            return True
        
        else:
            logger.error(f"Unsupported database type: {database_type}")
            return False
            
    except Exception as e:
        logger.error(f"Error creating user in database: {str(e)}")
        return False

def is_demo_mode() -> bool:
    """
    Check if the application is running in demo mode.
    
    Returns:
        bool: True if in demo mode, False otherwise
    """
    return os.getenv("DEMO_MODE", "").lower() in ("true", "1", "yes")
