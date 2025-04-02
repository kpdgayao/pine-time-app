"""
Test script to verify PostgreSQL connection and configuration.
This script attempts to connect to the PostgreSQL database using the configured
environment variables and performs basic operations to validate the connection.
"""

import os
import sys
import logging
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import create_engine, text

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("postgres_test")

# Load environment variables
load_dotenv()

def build_postgres_uri():
    """Build PostgreSQL URI from environment variables."""
    server = os.getenv("POSTGRES_SERVER")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db = os.getenv("POSTGRES_DB")
    port = os.getenv("POSTGRES_PORT", "5432")
    ssl_mode = os.getenv("POSTGRES_SSL_MODE", "require")
    
    # Log the connection details (except password)
    logger.info(f"PostgreSQL connection details:")
    logger.info(f"  Server: {server}")
    logger.info(f"  User: {user}")
    logger.info(f"  Database: {db}")
    logger.info(f"  Port: {port}")
    logger.info(f"  SSL Mode: {ssl_mode}")
    
    # Construct connection string
    return f"postgresql://{user}:{password}@{server}:{port}/{db}?sslmode={ssl_mode}"

def test_connection():
    """Test connection to PostgreSQL database."""
    try:
        # Build connection URI
        postgres_uri = build_postgres_uri()
        logger.info("Attempting to connect to PostgreSQL database...")
        
        # Create engine
        engine = create_engine(postgres_uri)
        
        # Test connection
        with engine.connect() as conn:
            logger.info("Connection successful!")
            
            # Test simple query
            result = conn.execute(text("SELECT 1"))
            logger.info(f"Query result: {result.scalar()}")
            
            # Get database version
            result = conn.execute(text("SELECT version()"))
            logger.info(f"PostgreSQL version: {result.scalar()}")
            
            # List tables (if any)
            result = conn.execute(text(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public'"
            ))
            tables = [row[0] for row in result]
            logger.info(f"Tables in database: {tables}")
            
        return True
    
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        return False

def main():
    """Main entry point."""
    success = test_connection()
    if success:
        logger.info("PostgreSQL connection test passed!")
        return 0
    else:
        logger.error("PostgreSQL connection test failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
