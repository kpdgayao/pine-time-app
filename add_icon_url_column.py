"""
Script to add the missing icon_url column to the badges table in PostgreSQL.
This script uses SQLAlchemy to connect to the database and add the column.
"""

import os
import sys
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("db_fix")

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import database configuration
from app.core.config import settings
from app.db.session import engine

def add_icon_url_column():
    """Add the icon_url column to the badges table if it doesn't exist."""
    try:
        # Check if the column exists
        check_sql = text("""
            SELECT 1 
            FROM information_schema.columns 
            WHERE table_name='badges' AND column_name='icon_url'
        """)
        
        # Add the column if it doesn't exist
        add_column_sql = text("""
            ALTER TABLE badges ADD COLUMN IF NOT EXISTS icon_url VARCHAR;
            UPDATE badges SET icon_url = '/static/images/badges/default_badge.png' WHERE icon_url IS NULL;
        """)
        
        with engine.connect() as connection:
            # Check if column exists
            result = connection.execute(check_sql)
            column_exists = result.scalar() is not None
            
            if not column_exists:
                logger.info("Adding icon_url column to badges table...")
                connection.execute(add_column_sql)
                connection.commit()
                logger.info("Successfully added icon_url column to badges table")
            else:
                logger.info("icon_url column already exists in badges table")
                
        return True
    except SQLAlchemyError as e:
        logger.error(f"Database error: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("Starting database fix script...")
    success = add_icon_url_column()
    if success:
        logger.info("Database fix completed successfully")
    else:
        logger.error("Database fix failed")
