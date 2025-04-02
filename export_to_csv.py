"""
Export SQLite database tables to CSV files.
This script exports each table from the SQLite database to a CSV file,
which can then be imported into PostgreSQL.
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
logger = logging.getLogger("export_csv")

# Load environment variables
load_dotenv()

def get_sqlite_engine():
    """Create SQLite engine."""
    sqlite_url = os.getenv("SQLITE_DATABASE_URI", "sqlite:///./pine_time.db")
    logger.info(f"SQLite URL: {sqlite_url}")
    return create_engine(sqlite_url, connect_args={"check_same_thread": False})

def get_table_names(engine):
    """Get all table names from the database."""
    inspector = inspect(engine)
    return inspector.get_table_names()

def export_table_to_csv(engine, table_name, output_dir="csv_export"):
    """Export a table to a CSV file."""
    # Create output directory if it doesn't exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_file = os.path.join(output_dir, f"{table_name}.csv")
    
    try:
        # Get column names
        inspector = inspect(engine)
        columns = [col['name'] for col in inspector.get_columns(table_name)]
        
        # Query data
        with engine.connect() as conn:
            result = conn.execute(text(f"SELECT * FROM {table_name}"))
            rows = list(result)
        
        # Write to CSV
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(columns)  # Write header
            for row in rows:
                writer.writerow(row)
        
        logger.info(f"Exported {len(rows)} rows from {table_name} to {output_file}")
        return True
    
    except Exception as e:
        logger.error(f"Error exporting table {table_name}: {e}")
        return False

def main():
    """Main function."""
    try:
        # Create engine
        sqlite_engine = get_sqlite_engine()
        
        # Get table names
        tables = get_table_names(sqlite_engine)
        logger.info(f"Found tables: {tables}")
        
        # Export each table
        success_count = 0
        for table in tables:
            if export_table_to_csv(sqlite_engine, table):
                success_count += 1
        
        logger.info(f"Successfully exported {success_count}/{len(tables)} tables")
        
        if success_count == len(tables):
            logger.info("Export completed successfully!")
            return 0
        else:
            logger.error("Export failed for some tables")
            return 1
    
    except Exception as e:
        logger.error(f"Export failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
