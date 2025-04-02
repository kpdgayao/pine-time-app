"""
Script to check the current state of both SQLite and PostgreSQL databases.
This will help us understand what tables and data exist in each database.
"""

import os
import sys
import logging
import json
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import create_engine, text, inspect

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("db_state.log")
    ]
)
logger = logging.getLogger("db_state")

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

def get_table_info(engine, db_type):
    """Get information about tables in the database."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    logger.info(f"{db_type} tables: {tables}")
    
    table_info = {}
    for table in tables:
        columns = inspector.get_columns(table)
        column_names = [col['name'] for col in columns]
        
        # Get row count
        try:
            with engine.connect() as conn:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                row_count = result.scalar()
        except Exception as e:
            logger.error(f"Error getting row count for {db_type} table {table}: {e}")
            row_count = "Error"
        
        table_info[table] = {
            "columns": column_names,
            "row_count": row_count
        }
    
    return table_info

def check_postgres_sequences():
    """Check the state of PostgreSQL sequences."""
    try:
        pg_engine = get_postgres_engine()
        with pg_engine.connect() as conn:
            # Get all sequences
            result = conn.execute(text("""
                SELECT 
                    sequence_name, 
                    last_value, 
                    start_value, 
                    increment_by, 
                    max_value, 
                    min_value, 
                    is_cycled 
                FROM 
                    information_schema.sequences 
                WHERE 
                    sequence_schema = 'public'
            """))
            
            sequences = []
            for row in result:
                sequences.append(dict(zip(result.keys(), row)))
            
            logger.info(f"PostgreSQL sequences: {json.dumps(sequences, indent=2)}")
            
            # Check sequence values vs table max IDs
            for seq in sequences:
                seq_name = seq['sequence_name']
                # Try to extract table name from sequence name (assuming standard naming)
                table_name = seq_name.replace('_id_seq', '')
                
                try:
                    result = conn.execute(text(f"SELECT COALESCE(MAX(id), 0) FROM {table_name}"))
                    max_id = result.scalar()
                    logger.info(f"Table {table_name} max ID: {max_id}, Sequence {seq_name} last value: {seq['last_value']}")
                except Exception as e:
                    logger.error(f"Error checking max ID for table {table_name}: {e}")
    
    except Exception as e:
        logger.error(f"Error checking PostgreSQL sequences: {e}")

def main():
    """Main function."""
    try:
        # Create engines
        sqlite_engine = get_sqlite_engine()
        pg_engine = get_postgres_engine()
        
        # Get table information
        sqlite_info = get_table_info(sqlite_engine, "SQLite")
        pg_info = get_table_info(pg_engine, "PostgreSQL")
        
        # Log detailed information
        logger.info(f"SQLite tables info: {json.dumps(sqlite_info, indent=2)}")
        logger.info(f"PostgreSQL tables info: {json.dumps(pg_info, indent=2)}")
        
        # Check common tables
        common_tables = set(sqlite_info.keys()).intersection(set(pg_info.keys()))
        logger.info(f"Common tables: {common_tables}")
        
        for table in common_tables:
            sqlite_cols = set(sqlite_info[table]["columns"])
            pg_cols = set(pg_info[table]["columns"])
            common_cols = sqlite_cols.intersection(pg_cols)
            
            logger.info(f"Table {table}:")
            logger.info(f"  SQLite: {sqlite_info[table]['row_count']} rows, {len(sqlite_cols)} columns")
            logger.info(f"  PostgreSQL: {pg_info[table]['row_count']} rows, {len(pg_cols)} columns")
            logger.info(f"  Common columns: {len(common_cols)}/{len(sqlite_cols)}")
            
            if sqlite_cols != pg_cols:
                sqlite_only = sqlite_cols - pg_cols
                pg_only = pg_cols - sqlite_cols
                
                if sqlite_only:
                    logger.info(f"  Columns only in SQLite: {sqlite_only}")
                if pg_only:
                    logger.info(f"  Columns only in PostgreSQL: {pg_only}")
        
        # Check PostgreSQL sequences
        check_postgres_sequences()
        
        logger.info("Database state check completed")
        return 0
    
    except Exception as e:
        logger.error(f"Database state check failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
