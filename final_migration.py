"""
Final migration script to ensure all data is properly transferred from SQLite to PostgreSQL.
This script focuses on fixing any discrepancies between the two databases.
"""

import os
import sys
import logging
import json
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import create_engine, text, inspect, MetaData, Table
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("final_migration.log")
    ]
)
logger = logging.getLogger("final_migration")

# Load environment variables
load_dotenv()

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

def clear_table(engine, table_name):
    """Clear all data from a table."""
    try:
        with engine.connect() as conn:
            conn.execute(text(f"DELETE FROM {table_name}"))
            conn.commit()
            logger.info(f"Cleared table: {table_name}")
            return True
    except Exception as e:
        logger.error(f"Error clearing table {table_name}: {e}")
        return False

def get_table_data(engine, table_name):
    """Get all data from a table as a list of dictionaries."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table_name}"))
            rows = []
            for row in result:
                # Convert row to dictionary
                row_dict = {}
                for idx, col in enumerate(result.keys()):
                    row_dict[col] = row[idx]
                rows.append(row_dict)
            return rows
    except Exception as e:
        logger.error(f"Error getting data from {table_name}: {e}")
        return []

def insert_row(engine, table_name, row_data):
    """Insert a single row into a table."""
    try:
        # Create column string and value placeholders
        columns = ", ".join(row_data.keys())
        placeholders = ", ".join([f":{col}" for col in row_data.keys()])
        
        # Create insert statement
        insert_stmt = text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})")
        
        # Execute insert
        with engine.connect() as conn:
            conn.execute(insert_stmt, row_data)
            conn.commit()
            return True
    except Exception as e:
        logger.error(f"Error inserting row into {table_name}: {e}")
        logger.error(f"Row data: {json.dumps(row_data, default=str)}")
        return False

def reset_sequence(engine, table_name):
    """Reset sequence for a table in PostgreSQL."""
    try:
        with engine.connect() as conn:
            # Get the sequence name
            result = conn.execute(text(
                f"SELECT pg_get_serial_sequence('{table_name}', 'id')"
            ))
            sequence_name = result.scalar()
            
            if sequence_name:
                # Get max ID
                result = conn.execute(text(f"SELECT COALESCE(MAX(id), 0) FROM {table_name}"))
                max_id = result.scalar()
                
                # Reset sequence
                conn.execute(text(f"ALTER SEQUENCE {sequence_name} RESTART WITH {max_id + 1}"))
                conn.commit()
                logger.info(f"Reset sequence for table {table_name} to {max_id + 1}")
                return True
            else:
                logger.warning(f"No sequence found for table {table_name}")
                return False
    except Exception as e:
        logger.error(f"Error resetting sequence for table {table_name}: {e}")
        return False

def migrate_table(sqlite_engine, pg_engine, table_name, clear_first=True):
    """Migrate a single table from SQLite to PostgreSQL."""
    logger.info(f"Migrating table: {table_name}")
    
    # Clear target table if requested
    if clear_first:
        if not clear_table(pg_engine, table_name):
            logger.error(f"Failed to clear table {table_name}, aborting migration")
            return False
    
    # Get data from SQLite
    sqlite_data = get_table_data(sqlite_engine, table_name)
    if not sqlite_data:
        logger.warning(f"No data found in SQLite table {table_name}")
        return True
    
    logger.info(f"Found {len(sqlite_data)} rows in SQLite table {table_name}")
    
    # Insert data into PostgreSQL
    success_count = 0
    for row in sqlite_data:
        if insert_row(pg_engine, table_name, row):
            success_count += 1
    
    logger.info(f"Successfully inserted {success_count}/{len(sqlite_data)} rows into {table_name}")
    
    # Reset sequence
    if not reset_sequence(pg_engine, table_name):
        logger.warning(f"Failed to reset sequence for table {table_name}")
    
    # Verify migration
    pg_data = get_table_data(pg_engine, table_name)
    logger.info(f"After migration: {len(pg_data)} rows in PostgreSQL table {table_name}")
    
    if len(sqlite_data) == len(pg_data):
        logger.info(f"Migration successful for table {table_name}")
        return True
    else:
        logger.error(f"Migration verification failed for table {table_name}: {len(sqlite_data)} rows in SQLite, {len(pg_data)} rows in PostgreSQL")
        return False

def main():
    """Main migration function."""
    try:
        # Create engines
        sqlite_engine = get_sqlite_engine()
        pg_engine = get_postgres_engine()
        
        # Define migration order (respecting foreign key constraints)
        tables = ["user", "event", "registration", "badge", "pointstransaction"]
        
        # Migrate each table
        success = True
        for table in tables:
            if not migrate_table(sqlite_engine, pg_engine, table, clear_first=True):
                logger.error(f"Migration failed for table {table}")
                success = False
        
        if success:
            logger.info("Migration completed successfully!")
            return 0
        else:
            logger.error("Migration failed for one or more tables")
            return 1
    
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
