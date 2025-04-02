"""
Simple migration script to transfer data from SQLite to PostgreSQL.
This script focuses solely on transferring data between existing tables.
"""

import os
import sys
import logging
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import create_engine, MetaData, Table, inspect, text
from sqlalchemy.orm import sessionmaker, Session

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("simple_migration")

# Load environment variables
load_dotenv()

# Add app directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import models
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

def clear_table(session, table_name):
    """Clear all data from a table."""
    try:
        session.execute(text(f"DELETE FROM {table_name}"))
        session.commit()
        logger.info(f"Cleared table: {table_name}")
    except Exception as e:
        logger.error(f"Error clearing table {table_name}: {e}")
        session.rollback()

def reset_sequence(pg_session, table_name):
    """Reset sequence for a table in PostgreSQL."""
    try:
        # Get the sequence name
        result = pg_session.execute(text(
            f"SELECT pg_get_serial_sequence('{table_name}', 'id')"
        ))
        sequence_name = result.scalar()
        
        if sequence_name:
            # Get max ID
            result = pg_session.execute(text(f"SELECT COALESCE(MAX(id), 0) FROM {table_name}"))
            max_id = result.scalar()
            
            # Reset sequence
            pg_session.execute(text(f"ALTER SEQUENCE {sequence_name} RESTART WITH {max_id + 1}"))
            pg_session.commit()
            logger.info(f"Reset sequence for table {table_name} to {max_id + 1}")
    except Exception as e:
        logger.error(f"Error resetting sequence for table {table_name}: {e}")
        pg_session.rollback()

def transfer_table_data(sqlite_session, pg_session, model):
    """Transfer data from SQLite to PostgreSQL for a specific model."""
    table_name = model.__tablename__
    logger.info(f"Transferring data for table: {table_name}")
    
    try:
        # Clear target table first
        clear_table(pg_session, table_name)
        
        # Get all records from SQLite
        records = sqlite_session.query(model).all()
        logger.info(f"Found {len(records)} records in SQLite {table_name} table")
        
        if not records:
            logger.info(f"No data to transfer for {table_name}")
            return
        
        # Convert to dictionaries
        record_dicts = []
        for record in records:
            record_dict = {c.name: getattr(record, c.name) for c in model.__table__.columns}
            record_dicts.append(record_dict)
        
        # Insert into PostgreSQL
        if record_dicts:
            pg_session.execute(model.__table__.insert(), record_dicts)
            pg_session.commit()
            logger.info(f"Inserted {len(record_dicts)} records into PostgreSQL {table_name} table")
        
        # Reset sequence
        reset_sequence(pg_session, table_name)
        
    except Exception as e:
        logger.error(f"Error transferring data for {table_name}: {e}")
        pg_session.rollback()
        raise

def verify_data(sqlite_session, pg_session, model):
    """Verify data was transferred correctly."""
    table_name = model.__tablename__
    
    try:
        sqlite_count = sqlite_session.query(model).count()
        pg_count = pg_session.query(model).count()
        
        if sqlite_count == pg_count:
            logger.info(f"Verification passed for {table_name}: {sqlite_count} records in both databases")
            return True
        else:
            logger.error(f"Verification failed for {table_name}: {sqlite_count} in SQLite, {pg_count} in PostgreSQL")
            return False
    except Exception as e:
        logger.error(f"Error verifying data for {table_name}: {e}")
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
        
        # Transfer data for each model
        for model in models:
            transfer_table_data(sqlite_session, pg_session, model)
        
        # Verify data transfer
        all_verified = True
        for model in models:
            if not verify_data(sqlite_session, pg_session, model):
                all_verified = False
        
        if all_verified:
            logger.info("Migration completed successfully! All data verified.")
        else:
            logger.error("Migration completed with verification errors.")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
    finally:
        # Close sessions
        sqlite_session.close()
        pg_session.close()

if __name__ == "__main__":
    main()
