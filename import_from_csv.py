"""
Import CSV files into PostgreSQL database.
This script imports data from CSV files into the PostgreSQL database tables.
"""

import os
import sys
import csv
import logging
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import create_engine, text, inspect, MetaData, Table

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("import_csv")

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
            return True
    except Exception as e:
        logger.error(f"Error clearing table {table_name}: {e}")
        return False

def disable_foreign_keys(engine):
    """Disable foreign key constraints in PostgreSQL."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SET session_replication_role = 'replica';"))
            conn.commit()
            logger.info("Disabled foreign key constraints")
            return True
    except Exception as e:
        logger.error(f"Error disabling foreign key constraints: {e}")
        return False

def enable_foreign_keys(engine):
    """Re-enable foreign key constraints in PostgreSQL."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SET session_replication_role = 'origin';"))
            conn.commit()
            logger.info("Re-enabled foreign key constraints")
            return True
    except Exception as e:
        logger.error(f"Error re-enabling foreign key constraints: {e}")
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
        
        # Get column information
        inspector = inspect(engine)
        columns = inspector.get_columns(table_name)
        column_types = {col['name']: col['type'] for col in columns}
        
        # Insert data
        with engine.connect() as conn:
            # Prepare batch insert
            metadata = MetaData()
            table = Table(table_name, metadata, autoload_with=engine)
            
            # Insert rows
            for row in rows:
                # Convert row to dictionary with proper types
                row_dict = {}
                for i, col_name in enumerate(headers):
                    if i < len(row):
                        # Handle empty values
                        if row[i] == '':
                            row_dict[col_name] = None
                        else:
                            row_dict[col_name] = row[i]
                
                # Insert row
                conn.execute(table.insert().values(**row_dict))
            
            conn.commit()
        
        logger.info(f"Successfully imported {len(rows)} rows into {table_name}")
        return True
    
    except Exception as e:
        logger.error(f"Error importing data into {table_name}: {e}")
        return False

def main():
    """Main function."""
    try:
        # Create engine
        pg_engine = get_postgres_engine()
        
        # Get table names
        tables = get_table_names(pg_engine)
        logger.info(f"Found tables: {tables}")
        
        # Define import order (respecting foreign key constraints)
        import_order = ['user', 'event', 'registration', 'badge', 'pointstransaction']
        
        # Filter tables to import
        tables_to_import = []
        for table in import_order:
            if table in tables:
                tables_to_import.append(table)
        
        # Add any remaining tables
        for table in tables:
            if table not in tables_to_import:
                tables_to_import.append(table)
        
        logger.info(f"Tables to import: {tables_to_import}")
        
        # Disable foreign key constraints
        disable_foreign_keys(pg_engine)
        
        # Import each table
        success_count = 0
        for table in tables_to_import:
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
        
        # Re-enable foreign key constraints
        enable_foreign_keys(pg_engine)
        
        logger.info(f"Successfully imported {success_count}/{len(tables_to_import)} tables")
        
        if success_count == len(tables_to_import):
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
