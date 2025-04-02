"""
ORM-based migration script for SQLite to PostgreSQL.
This script uses SQLAlchemy ORM to transfer data between databases,
ensuring proper data type handling and relationship maintenance.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("orm_migration.log")
    ]
)
logger = logging.getLogger("orm_migration")

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import SQLAlchemy components
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from app.db.base import Base
from app.models.user import User
from app.models.event import Event
from app.models.registration import Registration
from app.models.badge import Badge
from app.models.points import PointsTransaction

def get_sqlite_engine():
    """Create SQLite engine."""
    sqlite_url = os.getenv("SQLITE_DATABASE_URI", "sqlite:///./pine_time.db")
    logger.info(f"SQLite URL: {sqlite_url}")
    return create_engine(sqlite_url, connect_args={"check_same_thread": False})

def get_postgres_engine():
    """Create PostgreSQL engine."""
    server = os.getenv("POSTGRES_SERVER")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db = os.getenv("POSTGRES_DB")
    port = os.getenv("POSTGRES_PORT", "5432")
    ssl_mode = os.getenv("POSTGRES_SSL_MODE", "require")
    
    postgres_uri = f"postgresql://{user}:{password}@{server}:{port}/{db}?sslmode={ssl_mode}"
    logger.info(f"PostgreSQL URI constructed (credentials hidden)")
    return create_engine(postgres_uri)

def get_session(engine):
    """Create a database session."""
    Session = sessionmaker(bind=engine)
    return Session()

def clear_table(session, model):
    """Clear all data from a table."""
    try:
        session.query(model).delete()
        session.commit()
        logger.info(f"Cleared table: {model.__tablename__}")
        return True
    except Exception as e:
        logger.error(f"Error clearing table {model.__tablename__}: {e}")
        session.rollback()
        return False

def migrate_model(sqlite_session, pg_session, model):
    """Migrate data for a specific model."""
    table_name = model.__tablename__
    logger.info(f"Migrating data for table: {table_name}")
    
    try:
        # Get all records from SQLite
        records = sqlite_session.query(model).all()
        logger.info(f"Found {len(records)} records in SQLite {table_name} table")
        
        if not records:
            logger.info(f"No data to migrate for {table_name}")
            return True
        
        # Clear target table
        clear_table(pg_session, model)
        
        # Insert records into PostgreSQL
        success_count = 0
        for record in records:
            try:
                # Create a new instance with the same attributes
                new_record = model()
                for column in model.__table__.columns:
                    col_name = column.name
                    setattr(new_record, col_name, getattr(record, col_name))
                
                # Add to session
                pg_session.add(new_record)
                success_count += 1
            except Exception as e:
                logger.error(f"Error migrating record for {table_name}: {e}")
        
        # Commit changes
        pg_session.commit()
        logger.info(f"Successfully migrated {success_count}/{len(records)} records for {table_name}")
        
        return success_count == len(records)
    
    except Exception as e:
        logger.error(f"Error migrating data for {table_name}: {e}")
        pg_session.rollback()
        return False

def verify_migration(sqlite_session, pg_session, model):
    """Verify migration for a specific model."""
    table_name = model.__tablename__
    logger.info(f"Verifying migration for table: {table_name}")
    
    try:
        # Get counts from both databases
        sqlite_count = sqlite_session.query(model).count()
        pg_count = pg_session.query(model).count()
        
        if sqlite_count == pg_count:
            logger.info(f"Verification passed for {table_name}: {sqlite_count} records in both databases")
            return True
        else:
            logger.error(f"Verification failed for {table_name}: {sqlite_count} records in SQLite, {pg_count} records in PostgreSQL")
            return False
    
    except Exception as e:
        logger.error(f"Error verifying migration for {table_name}: {e}")
        return False

def main():
    """Main migration function."""
    try:
        # Create engines
        sqlite_engine = get_sqlite_engine()
        pg_engine = get_postgres_engine()
        
        # Create sessions
        sqlite_session = get_session(sqlite_engine)
        pg_session = get_session(pg_engine)
        
        # Define models in order of dependency
        models = [User, Event, Registration, Badge, PointsTransaction]
        
        # Migrate each model
        success = True
        for model in models:
            if not migrate_model(sqlite_session, pg_session, model):
                logger.error(f"Migration failed for {model.__tablename__}")
                success = False
        
        # Verify migration
        all_verified = True
        for model in models:
            if not verify_migration(sqlite_session, pg_session, model):
                all_verified = False
        
        # Close sessions
        sqlite_session.close()
        pg_session.close()
        
        if success and all_verified:
            logger.info("Migration completed successfully!")
            return 0
        else:
            logger.error("Migration failed or verification failed")
            return 1
    
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
