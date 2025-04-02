"""
Single table migration script with detailed logging.
This script focuses on migrating a single table with detailed logging to help diagnose issues.
"""

import os
import sys
import logging
import argparse
import json
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import create_engine, text, inspect

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("single_table_migration.log")
    ]
)
logger = logging.getLogger("single_table")

# Load environment variables
load_dotenv()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Migrate a single table from SQLite to PostgreSQL")
    parser.add_argument(
        "table", 
        help="Table name to migrate"
    )
    parser.add_argument(
        "--clear", 
        action="store_true",
        help="Clear target table before migration"
    )
    return parser.parse_args()

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

def get_table_columns(engine, table_name):
    """Get column information for a table."""
    inspector = inspect(engine)
    return inspector.get_columns(table_name)

def clear_table(engine, table_name):
    """Clear all data from a table."""
    try:
        with engine.connect() as conn:
            conn.execute(text(f"DELETE FROM {table_name}"))
            conn.commit()
            logger.info(f"Cleared table: {table_name}")
    except Exception as e:
        logger.error(f"Error clearing table {table_name}: {e}")

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
    except Exception as e:
        logger.error(f"Error resetting sequence for table {table_name}: {e}")

def get_table_data(engine, table_name):
    """Get all data from a table."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table_name}"))
            columns = result.keys()
            rows = []
            for row in result:
                rows.append(dict(zip(columns, row)))
            return rows
    except Exception as e:
        logger.error(f"Error getting data from table {table_name}: {e}")
        return []

def insert_data(engine, table_name, data):
    """Insert data into a table."""
    if not data:
        logger.info(f"No data to insert into {table_name}")
        return 0
    
    try:
        with engine.connect() as conn:
            # Get column information
            inspector = inspect(engine)
            columns = inspector.get_columns(table_name)
            column_names = [col['name'] for col in columns]
            
            # Filter data to only include existing columns
            filtered_data = []
            for row in data:
                filtered_row = {k: v for k, v in row.items() if k in column_names}
                filtered_data.append(filtered_row)
            
            # Insert data
            if filtered_data:
                # Convert to list of tuples for executemany
                column_names = list(filtered_data[0].keys())
                values = []
                for row in filtered_data:
                    values.append(tuple(row.get(col) for col in column_names))
                
                # Build insert statement
                placeholders = ", ".join([f":{i}" for i in range(len(column_names))])
                columns_str = ", ".join(column_names)
                
                # Log the first row for debugging
                logger.debug(f"First row to insert: {json.dumps(filtered_data[0], default=str)}")
                
                # Insert data one row at a time for better error handling
                inserted = 0
                for row in filtered_data:
                    try:
                        # Build insert statement for this row
                        columns_str = ", ".join(row.keys())
                        placeholders = ", ".join([f":{col}" for col in row.keys()])
                        insert_stmt = text(f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})")
                        
                        # Execute insert
                        conn.execute(insert_stmt, row)
                        inserted += 1
                    except Exception as e:
                        logger.error(f"Error inserting row: {e}")
                        logger.debug(f"Problematic row: {json.dumps(row, default=str)}")
                
                conn.commit()
                logger.info(f"Inserted {inserted}/{len(filtered_data)} rows into {table_name}")
                return inserted
            else:
                logger.warning(f"No valid data to insert into {table_name}")
                return 0
    except Exception as e:
        logger.error(f"Error inserting data into table {table_name}: {e}")
        return 0

def migrate_table(sqlite_engine, pg_engine, table_name, clear=False):
    """Migrate a single table from SQLite to PostgreSQL."""
    logger.info(f"Migrating table: {table_name}")
    
    # Get column information
    sqlite_columns = get_table_columns(sqlite_engine, table_name)
    pg_columns = get_table_columns(pg_engine, table_name)
    
    logger.info(f"SQLite columns: {[col['name'] for col in sqlite_columns]}")
    logger.info(f"PostgreSQL columns: {[col['name'] for col in pg_columns]}")
    
    # Clear target table if requested
    if clear:
        clear_table(pg_engine, table_name)
    
    # Get data from SQLite
    data = get_table_data(sqlite_engine, table_name)
    logger.info(f"Found {len(data)} rows in SQLite table {table_name}")
    
    # Insert data into PostgreSQL
    inserted = insert_data(pg_engine, table_name, data)
    
    # Reset sequence
    reset_sequence(pg_engine, table_name)
    
    # Verify data
    pg_data = get_table_data(pg_engine, table_name)
    logger.info(f"Found {len(pg_data)} rows in PostgreSQL table {table_name} after migration")
    
    if len(data) == len(pg_data):
        logger.info(f"Migration successful for table {table_name}: {len(data)} rows migrated")
        return True
    else:
        logger.error(f"Migration verification failed for table {table_name}: {len(data)} rows in SQLite, {len(pg_data)} rows in PostgreSQL")
        return False

def main():
    """Main function."""
    args = parse_args()
    
    try:
        # Create engines
        sqlite_engine = get_sqlite_engine()
        pg_engine = get_postgres_engine()
        
        # Migrate table
        success = migrate_table(sqlite_engine, pg_engine, args.table, args.clear)
        
        if success:
            logger.info(f"Migration of table {args.table} completed successfully")
            return 0
        else:
            logger.error(f"Migration of table {args.table} failed")
            return 1
    
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
