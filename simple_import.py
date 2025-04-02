"""
Simple CSV import script for PostgreSQL.
This script imports data from CSV files into PostgreSQL tables without
requiring special permissions to disable foreign key constraints.
"""

import os
import sys
import csv
import logging
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import create_engine, text, inspect

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("simple_import")

# Load environment variables
load_dotenv()

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

def import_csv_to_table(engine, table_name, csv_file):
    """Import data from a CSV file into a table."""
    try:
        # Read CSV file
        with open(csv_file, 'r', newline='') as f:
            reader = csv.reader(f)
            headers = next(reader)  # Read header row
            rows = list(reader)
        
        if not rows:
            logger.warning(f"No data found in CSV file {csv_file}")
            return True
        
        logger.info(f"Importing {len(rows)} rows into {table_name} from {csv_file}")
        
        # Insert data
        with engine.connect() as conn:
            # Insert rows one by one for better error handling
            success_count = 0
            for row in rows:
                try:
                    # Convert row to dictionary
                    row_dict = {}
                    for i, col_name in enumerate(headers):
                        if i < len(row):
                            # Handle empty values
                            if row[i] == '':
                                row_dict[col_name] = None
                            else:
                                row_dict[col_name] = row[i]
                    
                    # Build insert statement
                    columns = ", ".join(row_dict.keys())
                    placeholders = ", ".join([f":{col}" for col in row_dict.keys()])
                    insert_stmt = text(f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})")
                    
                    # Execute insert
                    conn.execute(insert_stmt, row_dict)
                    success_count += 1
                except Exception as e:
                    logger.error(f"Error inserting row into {table_name}: {e}")
                    logger.error(f"Row data: {row_dict}")
            
            conn.commit()
            logger.info(f"Successfully inserted {success_count}/{len(rows)} rows into {table_name}")
            return success_count > 0
    
    except Exception as e:
        logger.error(f"Error importing data into {table_name}: {e}")
        return False

def main():
    """Main function."""
    try:
        # Create engine
        pg_engine = get_postgres_engine()
        
        # Define import order (respecting foreign key constraints)
        # Import in reverse order to avoid foreign key constraint issues
        import_order = ['pointstransaction', 'badge', 'registration', 'event', 'user']
        
        # Import each table
        success_count = 0
        for table in import_order:
            csv_file = os.path.join("csv_export", f"{table}.csv")
            
            if not os.path.exists(csv_file):
                logger.warning(f"CSV file not found for table {table}: {csv_file}")
                continue
            
            # Clear table
            clear_table(pg_engine, table)
            
            # Import data
            if import_csv_to_table(pg_engine, table, csv_file):
                success_count += 1
                
                # Reset sequence
                reset_sequence(pg_engine, table)
        
        logger.info(f"Successfully imported {success_count}/{len(import_order)} tables")
        
        if success_count == len(import_order):
            logger.info("Import completed successfully!")
            return 0
        else:
            logger.error("Import failed for some tables")
            return 1
    
    except Exception as e:
        logger.error(f"Import failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
