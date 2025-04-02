"""
Table-by-table migration script for SQLite to PostgreSQL.
This script migrates data one table at a time with explicit column mapping
and handles potential data type issues between SQLite and PostgreSQL.
"""

import os
import sys
import logging
import argparse
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import sqlalchemy as sa
from sqlalchemy import create_engine, MetaData, Table, inspect, text
from sqlalchemy.orm import sessionmaker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("migration_detailed.log")
    ]
)
logger = logging.getLogger("table_migration")

# Load environment variables
load_dotenv()

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Migrate data from SQLite to PostgreSQL table by table")
    parser.add_argument(
        "--table", 
        help="Specific table to migrate (default: all tables)"
    )
    parser.add_argument(
        "--clear", 
        action="store_true",
        help="Clear target tables before migration"
    )
    parser.add_argument(
        "--verify", 
        action="store_true",
        help="Verify data after migration"
    )
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug logging"
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

def test_connection(engine, db_type):
    """Test database connection."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            logger.info(f"{db_type} connection successful")
            return True
    except Exception as e:
        logger.error(f"{db_type} connection failed: {e}")
        return False

def get_table_names(engine):
    """Get all table names from the database."""
    inspector = inspect(engine)
    return inspector.get_table_names()

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

def get_table_columns(engine, table_name):
    """Get column names for a table."""
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    return [col['name'] for col in columns]

def migrate_table(sqlite_engine, pg_engine, table_name, clear=False):
    """Migrate a single table from SQLite to PostgreSQL."""
    logger.info(f"Migrating table: {table_name}")
    
    try:
        # Get column names for both tables
        sqlite_columns = get_table_columns(sqlite_engine, table_name)
        pg_columns = get_table_columns(pg_engine, table_name)
        
        # Find common columns
        common_columns = list(set(sqlite_columns).intersection(set(pg_columns)))
        logger.info(f"Common columns for {table_name}: {common_columns}")
        
        if not common_columns:
            logger.error(f"No common columns found for table {table_name}")
            return False
        
        # Clear target table if requested
        if clear:
            clear_table(pg_engine, table_name)
        
        # Read data from SQLite
        query = f"SELECT {', '.join(common_columns)} FROM {table_name}"
        df = pd.read_sql(query, sqlite_engine)
        
        if df.empty:
            logger.info(f"No data found in SQLite table {table_name}")
            return True
        
        logger.info(f"Read {len(df)} rows from SQLite table {table_name}")
        
        # Handle data type conversions if needed
        for col in df.columns:
            # Convert datetime columns to proper format
            if df[col].dtype == 'object' and df[col].apply(lambda x: isinstance(x, str) and 'T' in x).any():
                try:
                    df[col] = pd.to_datetime(df[col])
                    logger.info(f"Converted column {col} to datetime")
                except:
                    pass
        
        # Write data to PostgreSQL
        df.to_sql(table_name, pg_engine, if_exists='append', index=False)
        logger.info(f"Wrote {len(df)} rows to PostgreSQL table {table_name}")
        
        # Reset sequence
        reset_sequence(pg_engine, table_name)
        
        return True
    
    except Exception as e:
        logger.error(f"Error migrating table {table_name}: {e}")
        return False

def verify_table(sqlite_engine, pg_engine, table_name):
    """Verify data was migrated correctly for a table."""
    try:
        with sqlite_engine.connect() as sqlite_conn, pg_engine.connect() as pg_conn:
            # Get row counts
            sqlite_count = sqlite_conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            pg_count = pg_conn.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            
            if sqlite_count == pg_count:
                logger.info(f"Verification passed for {table_name}: {sqlite_count} rows in both databases")
                return True
            else:
                logger.error(f"Verification failed for {table_name}: {sqlite_count} rows in SQLite, {pg_count} rows in PostgreSQL")
                return False
    except Exception as e:
        logger.error(f"Error verifying table {table_name}: {e}")
        return False

def main():
    """Main migration function."""
    args = parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger("table_migration").setLevel(logging.DEBUG)
    
    try:
        # Create engines
        sqlite_engine = get_sqlite_engine()
        pg_engine = get_postgres_engine()
        
        # Test connections
        if not test_connection(sqlite_engine, "SQLite"):
            logger.error("SQLite connection test failed, aborting migration")
            return 1
        
        if not test_connection(pg_engine, "PostgreSQL"):
            logger.error("PostgreSQL connection test failed, aborting migration")
            return 1
        
        # Get table names
        sqlite_tables = get_table_names(sqlite_engine)
        pg_tables = get_table_names(pg_engine)
        
        logger.info(f"SQLite tables: {sqlite_tables}")
        logger.info(f"PostgreSQL tables: {pg_tables}")
        
        # Find common tables
        common_tables = list(set(sqlite_tables).intersection(set(pg_tables)))
        logger.info(f"Common tables: {common_tables}")
        
        if not common_tables:
            logger.error("No common tables found between databases")
            return 1
        
        # Define migration order (respecting foreign key constraints)
        migration_order = ['user', 'event', 'registration', 'badge', 'pointstransaction']
        
        # Filter tables to migrate
        if args.table:
            if args.table in common_tables:
                tables_to_migrate = [args.table]
            else:
                logger.error(f"Table {args.table} not found in both databases")
                return 1
        else:
            # Sort tables according to migration order
            tables_to_migrate = []
            for table in migration_order:
                if table in common_tables:
                    tables_to_migrate.append(table)
            
            # Add any remaining common tables
            for table in common_tables:
                if table not in tables_to_migrate:
                    tables_to_migrate.append(table)
        
        logger.info(f"Tables to migrate: {tables_to_migrate}")
        
        # Migrate each table
        success_count = 0
        for table in tables_to_migrate:
            if migrate_table(sqlite_engine, pg_engine, table, args.clear):
                success_count += 1
        
        logger.info(f"Successfully migrated {success_count}/{len(tables_to_migrate)} tables")
        
        # Verify data if requested
        if args.verify:
            verified_count = 0
            for table in tables_to_migrate:
                if verify_table(sqlite_engine, pg_engine, table):
                    verified_count += 1
            
            logger.info(f"Successfully verified {verified_count}/{len(tables_to_migrate)} tables")
            
            if verified_count != len(tables_to_migrate):
                logger.error("Data verification failed for some tables")
                return 1
        
        logger.info("Migration completed successfully")
        return 0
    
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
