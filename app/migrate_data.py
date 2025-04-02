"""
Migration script to transfer data from SQLite to PostgreSQL.
This script connects to both databases, creates tables in PostgreSQL,
and transfers data while preserving relationships.
"""

import os
import sys
import time
import argparse
import logging
import traceback
from typing import Dict, List, Any, Optional, Union
from contextlib import contextmanager
from dotenv import load_dotenv

import sqlalchemy as sa
from sqlalchemy import create_engine, MetaData, Table, Column, inspect
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import text

# Load environment variables from .env file
load_dotenv()

# Add app directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import models and configuration
from app.db.base import Base
from app.models.user import User
from app.models.event import Event
from app.models.registration import Registration
from app.models.badge import Badge
from app.models.points import PointsTransaction
from app.core.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("migration.log")
    ]
)
logger = logging.getLogger("migration")

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Migrate data from SQLite to PostgreSQL")
    parser.add_argument(
        "--source", 
        default="sqlite:///./pine_time.db",
        help="Source database URI (SQLite)"
    )
    parser.add_argument(
        "--target", 
        help="Target database URI (PostgreSQL)"
    )
    parser.add_argument(
        "--batch-size", 
        type=int, 
        default=100,
        help="Batch size for data transfer"
    )
    parser.add_argument(
        "--verify", 
        action="store_true",
        help="Verify data integrity after migration"
    )
    parser.add_argument(
        "--drop-target", 
        action="store_true",
        help="Drop all tables in target database before migration (use with caution!)"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug logging"
    )
    return parser.parse_args()

@contextmanager
def get_session(engine):
    """Create a session and handle cleanup."""
    session_factory = sessionmaker(bind=engine)
    session = session_factory()
    try:
        yield session
    finally:
        session.close()

def get_table_names(engine) -> List[str]:
    """Get all table names from the database."""
    inspector = inspect(engine)
    return inspector.get_table_names()

def get_row_count(session: Session, table_name: str) -> int:
    """Get the number of rows in a table."""
    try:
        result = session.execute(text(f"SELECT COUNT(*) FROM {table_name}"))
        return result.scalar()
    except Exception as e:
        logger.error(f"Error getting row count for table {table_name}: {e}")
        return 0

def create_tables(engine):
    """Create all tables in the target database."""
    logger.info("Creating tables in target database...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Tables created successfully.")
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        logger.debug(traceback.format_exc())
        raise

def drop_tables(engine):
    """Drop all tables in the target database."""
    logger.info("Dropping all tables in target database...")
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("Tables dropped successfully.")
    except Exception as e:
        logger.error(f"Error dropping tables: {e}")
        logger.debug(traceback.format_exc())
        raise

def transfer_data(source_session: Session, target_session: Session, model, batch_size: int):
    """Transfer data for a specific model."""
    table_name = model.__tablename__
    logger.info(f"Transferring data for table: {table_name}")
    
    try:
        # Get total count for progress reporting
        total_count = get_row_count(source_session, table_name)
        if total_count == 0:
            logger.info(f"No data found in table {table_name}, skipping.")
            return
        
        logger.info(f"Found {total_count} rows in {table_name}")
        
        # Process in batches
        offset = 0
        while True:
            try:
                # Get batch of records
                records = source_session.query(model).order_by(model.id).offset(offset).limit(batch_size).all()
                if not records:
                    break
                
                # Convert to dictionaries
                record_dicts = []
                for record in records:
                    record_dict = {c.name: getattr(record, c.name) for c in model.__table__.columns}
                    record_dicts.append(record_dict)
                
                # Insert into target database
                if record_dicts:
                    logger.debug(f"Inserting {len(record_dicts)} records into {table_name}")
                    target_session.execute(model.__table__.insert(), record_dicts)
                    target_session.commit()
                
                # Update progress
                offset += len(records)
                progress = min(100, int(offset / total_count * 100))
                logger.info(f"Progress for {table_name}: {progress}% ({offset}/{total_count})")
            
            except Exception as e:
                logger.error(f"Error transferring batch for {table_name} at offset {offset}: {e}")
                logger.debug(traceback.format_exc())
                target_session.rollback()
                raise
        
        logger.info(f"Completed transfer for table: {table_name}")
    
    except Exception as e:
        logger.error(f"Error transferring data for {table_name}: {e}")
        logger.debug(traceback.format_exc())
        raise

def verify_data_integrity(source_session: Session, target_session: Session, model):
    """Verify data integrity for a specific model."""
    table_name = model.__tablename__
    logger.info(f"Verifying data integrity for table: {table_name}")
    
    try:
        # Get counts from both databases
        source_count = get_row_count(source_session, table_name)
        target_count = get_row_count(target_session, table_name)
        
        if source_count != target_count:
            logger.error(f"Data integrity check failed for {table_name}: Source has {source_count} rows, target has {target_count} rows")
            return False
        
        logger.info(f"Data integrity check passed for {table_name}: {source_count} rows in both databases")
        return True
    
    except Exception as e:
        logger.error(f"Error verifying data integrity for {table_name}: {e}")
        logger.debug(traceback.format_exc())
        return False

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

def run_migration(args):
    """Run the migration process."""
    start_time = time.time()
    
    try:
        # Create engines for source and target databases
        logger.info(f"Creating source engine for: {args.source}")
        source_engine = create_engine(args.source)
        
        # If target not specified, build it from environment variables
        if not args.target:
            postgres_uri = build_postgres_uri()
            logger.info(f"Using PostgreSQL URI from environment")
            target_engine = create_engine(postgres_uri)
        else:
            logger.info(f"Using specified target: {args.target}")
            target_engine = create_engine(args.target)
        
        # Check if source database is accessible
        try:
            logger.info("Testing connection to source database...")
            conn = source_engine.connect()
            conn.close()
            logger.info("Source database connection successful!")
        except Exception as e:
            logger.error(f"Failed to connect to source database: {e}")
            logger.debug(traceback.format_exc())
            return False
        
        # Check if target database is accessible
        try:
            logger.info("Testing connection to target database...")
            conn = target_engine.connect()
            conn.close()
            logger.info("Target database connection successful!")
        except Exception as e:
            logger.error(f"Failed to connect to target database: {e}")
            logger.debug(traceback.format_exc())
            return False
        
        # List tables in source database
        source_tables = get_table_names(source_engine)
        logger.info(f"Tables in source database: {source_tables}")
        
        # Drop tables in target database if requested
        if args.drop_target:
            drop_tables(target_engine)
        
        # Create tables in target database
        create_tables(target_engine)
        
        # List tables in target database after creation
        target_tables = get_table_names(target_engine)
        logger.info(f"Tables in target database after creation: {target_tables}")
        
        # Define the order of tables to migrate (respecting foreign key constraints)
        models = [User, Event, Registration, Badge, PointsTransaction]
        
        # Transfer data for each model
        with get_session(source_engine) as source_session, get_session(target_engine) as target_session:
            for model in models:
                try:
                    transfer_data(source_session, target_session, model, args.batch_size)
                except Exception as e:
                    logger.error(f"Failed to transfer data for model {model.__name__}: {e}")
                    return False
        
        # Verify data integrity if requested
        if args.verify:
            all_verified = True
            with get_session(source_engine) as source_session, get_session(target_engine) as target_session:
                for model in models:
                    if not verify_data_integrity(source_session, target_session, model):
                        all_verified = False
            
            if not all_verified:
                logger.error("Data integrity verification failed!")
                return False
        
        end_time = time.time()
        duration = end_time - start_time
        logger.info(f"Migration completed in {duration:.2f} seconds")
        return True
    
    except Exception as e:
        logger.error(f"Unexpected error during migration: {e}")
        logger.debug(traceback.format_exc())
        return False

def main():
    """Main entry point."""
    args = parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger("migration").setLevel(logging.DEBUG)
    
    logger.info(f"Source database: {args.source}")
    logger.info(f"Batch size: {args.batch_size}")
    logger.info(f"Verify: {args.verify}")
    logger.info(f"Drop target: {args.drop_target}")
    
    success = run_migration(args)
    if success:
        logger.info("Migration completed successfully!")
        return 0
    else:
        logger.error("Migration failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
