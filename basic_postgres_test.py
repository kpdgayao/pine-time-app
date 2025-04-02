"""
Basic PostgreSQL connection test.
This script tests the connection to the PostgreSQL database
without relying on the application's models.
"""

import os
import sys
from dotenv import load_dotenv
import sqlalchemy as sa
from sqlalchemy import create_engine, text

# Load environment variables
load_dotenv()

def get_postgres_uri():
    """Build PostgreSQL URI from environment variables."""
    server = os.getenv("POSTGRES_SERVER")
    user = os.getenv("POSTGRES_USER")
    password = os.getenv("POSTGRES_PASSWORD")
    db = os.getenv("POSTGRES_DB")
    port = os.getenv("POSTGRES_PORT", "5432")
    ssl_mode = os.getenv("POSTGRES_SSL_MODE", "require")
    
    # Construct connection string
    return f"postgresql://{user}:{password}@{server}:{port}/{db}?sslmode={ssl_mode}"

def main():
    """Test PostgreSQL connection and basic functionality."""
    try:
        # Get PostgreSQL URI
        postgres_uri = get_postgres_uri()
        print(f"Connecting to PostgreSQL database...")
        
        # Create engine
        engine = create_engine(postgres_uri)
        
        # Test connection
        with engine.connect() as conn:
            print("Connection successful!")
            
            # Get database version
            result = conn.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"PostgreSQL version: {version}")
            
            # List tables
            result = conn.execute(text(
                "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'"
            ))
            tables = [row[0] for row in result]
            print(f"Tables in database: {tables}")
            
            # Get row counts for each table
            for table in tables:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"Table {table}: {count} rows")
        
        print("PostgreSQL connection test completed successfully!")
        return 0
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
