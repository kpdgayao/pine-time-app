"""
PostgreSQL Sequence Reset Utility

This script resets PostgreSQL sequences to match the maximum ID values in their respective tables.
Use this after importing data to ensure sequence values are properly synchronized.
"""

import os
import sys
import logging
import argparse
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import create_engine, text, inspect

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("sequence_reset.log")
    ]
)
logger = logging.getLogger("sequence_reset")

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

def get_tables_with_id_column(engine):
    """Get all tables that have an 'id' column."""
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    tables_with_id = []
    for table in tables:
        columns = inspector.get_columns(table)
        column_names = [col['name'] for col in columns]
        if 'id' in column_names:
            tables_with_id.append(table)
    
    return tables_with_id

def get_sequences(engine):
    """Get all sequences in the database."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT 
                sequence_name 
            FROM 
                information_schema.sequences 
            WHERE 
                sequence_schema = 'public'
        """))
        
        return [row[0] for row in result]

def reset_sequence(engine, table_name, sequence_name, dry_run=False):
    """Reset a sequence to match the maximum ID in its table."""
    try:
        with engine.connect() as conn:
            # Get the maximum ID from the table
            result = conn.execute(text(f"SELECT COALESCE(MAX(id), 0) FROM {table_name}"))
            max_id = result.scalar()
            
            # Get current sequence value
            result = conn.execute(text(f"SELECT last_value FROM {sequence_name}"))
            current_value = result.scalar()
            
            logger.info(f"Table {table_name}: Max ID = {max_id}, Current sequence value = {current_value}")
            
            # Only reset if needed
            if max_id >= current_value or current_value == 1:  # Also reset if sequence is at initial value
                next_value = max_id + 1
                if not dry_run:
                    # Reset the sequence to max_id + 1
                    conn.execute(text(f"ALTER SEQUENCE {sequence_name} RESTART WITH {next_value}"))
                    logger.info(f"Reset sequence {sequence_name} to {next_value}")
                else:
                    logger.info(f"[DRY RUN] Would reset sequence {sequence_name} to {next_value}")
                return True, f"Reset {sequence_name} to {next_value}"
            else:
                logger.info(f"Sequence {sequence_name} already ahead of max ID, no reset needed")
                return False, f"No reset needed for {sequence_name}"
                
    except Exception as e:
        logger.error(f"Error resetting sequence {sequence_name}: {e}")
        return False, f"Error: {str(e)}"

def reset_all_sequences(engine, dry_run=False):
    """Reset all sequences to match their table's maximum ID."""
    tables = get_tables_with_id_column(engine)
    sequences = get_sequences(engine)
    
    results = []
    
    for table in tables:
        # Try to find a matching sequence using common naming patterns
        sequence_candidates = [
            f"{table}_id_seq",  # Standard naming
            f"{table}_seq",     # Alternative naming
            f"{table}s_id_seq"  # Plural form
        ]
        
        matched_sequence = None
        for candidate in sequence_candidates:
            if candidate in sequences:
                matched_sequence = candidate
                break
        
        if matched_sequence:
            success, message = reset_sequence(engine, table, matched_sequence, dry_run)
            results.append((table, matched_sequence, success, message))
        else:
            logger.warning(f"No matching sequence found for table {table}")
            results.append((table, None, False, "No matching sequence found"))
    
    return results

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Reset PostgreSQL sequences to match table max IDs")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    args = parser.parse_args()
    
    try:
        # Create engine
        engine = get_postgres_engine()
        
        # Reset sequences
        logger.info(f"Starting sequence reset {'(DRY RUN)' if args.dry_run else ''}")
        results = reset_all_sequences(engine, args.dry_run)
        
        # Print summary
        logger.info("Sequence reset summary:")
        for table, sequence, success, message in results:
            status = "SUCCESS" if success else "SKIPPED"
            logger.info(f"{status}: {table} -> {sequence or 'N/A'} - {message}")
        
        logger.info("Sequence reset completed")
        return 0
    
    except Exception as e:
        logger.error(f"Sequence reset failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
