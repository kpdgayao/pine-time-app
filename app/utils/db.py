"""
Database utilities for the Pine Time backend.
Handles database connection management and configuration.
(Copied from admin_dashboard/utils/db.py for backend use)
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
    Includes validation of required parameters for PostgreSQL.
    Returns:
        dict: Database configuration with validated parameters
    """
    database_type = os.getenv("DATABASE_TYPE", "sqlite").lower()
    if database_type == "postgresql":
        config = {
            "database_type": "postgresql",
            "server": os.getenv("POSTGRES_SERVER", "localhost"),
            "user": os.getenv("POSTGRES_USER", "postgres"),
            "password": os.getenv("POSTGRES_PASSWORD", ""),
            "db": os.getenv("POSTGRES_DB", "postgres"),
            "port": os.getenv("POSTGRES_PORT", "5432"),
            "ssl_mode": os.getenv("POSTGRES_SSL_MODE", "prefer"),
            "pool_size": int(os.getenv("POOL_SIZE", "5")),
            "max_overflow": int(os.getenv("MAX_OVERFLOW", "10")),
            "pool_timeout": int(os.getenv("POOL_TIMEOUT", "30")),
            "pool_recycle": int(os.getenv("POOL_RECYCLE", "1800")),
            "pool_pre_ping": os.getenv("POOL_PRE_PING", "True").lower() == "true",
        }
        # Log configuration (without password)
        logger.info(f"Using PostgreSQL config: {{k: v for k, v in config.items() if k != 'password'}}")
        return config
    else:
        raise ValueError("Only PostgreSQL is supported for backend deployment.")

def get_database_uri() -> str:
    """
    Get database URI based on configuration.
    Returns:
        str: Database URI
    """
    config = get_database_config()
    user = config["user"]
    password = config["password"]
    server = config["server"]
    port = config["port"]
    db = config["db"]
    ssl_mode = config["ssl_mode"]
    return f"postgresql://{user}:{password}@{server}:{port}/{db}?sslmode={ssl_mode}"

def get_postgres_connection_params() -> Dict[str, Any]:
    """
    Get PostgreSQL connection parameters from environment variables.
    Returns:
        Dict[str, Any]: Dictionary with connection parameters
    """
    config = get_database_config()
    params = {
        "host": config["server"],
        "user": config["user"],
        "password": config["password"],
        "dbname": config["db"],
        "port": config["port"],
        "sslmode": config["ssl_mode"],
    }
    return params

def is_demo_mode() -> bool:
    """
    Check if the application is running in demo mode.
    Returns:
        bool: True if in demo mode, False otherwise
    """
    return os.getenv("DEMO_MODE", "false").lower() == "true"
