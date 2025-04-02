"""
Simple script to test the Neon PostgreSQL connection.
"""

import os
import sys
import logging
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("db_test")

# Load environment variables
load_dotenv()

def test_connection():
    """Test connection to Neon PostgreSQL."""
    # Get connection parameters from environment variables
    server = os.getenv("POSTGRES_SERVER")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db = os.getenv("POSTGRES_DB")
    port = os.getenv("POSTGRES_PORT", "5432")
    ssl_mode = os.getenv("POSTGRES_SSL_MODE", "require")
    
    # Construct connection string
    conn_str = f"postgresql://{user}:{password}@{server}:{port}/{db}?sslmode={ssl_mode}"
    
    logger.info(f"Testing connection to: {server}")
    logger.info(f"Database: {db}")
    logger.info(f"User: {user}")
    logger.info(f"SSL Mode: {ssl_mode}")
    
    try:
        # Create engine
        engine = create_engine(conn_str)
        
        # Try to connect
        with engine.connect() as conn:
            # Execute a simple query
            result = conn.execute(text("SELECT 1"))
            value = result.scalar()
            logger.info(f"Connection successful! Test query result: {value}")
            return True
    except Exception as e:
        logger.error(f"Connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()
