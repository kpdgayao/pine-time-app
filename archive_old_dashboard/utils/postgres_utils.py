"""
PostgreSQL utilities for the Pine Time Admin Dashboard.
Handles PostgreSQL-specific operations, connection pooling, and error handling.
"""

import os
import logging
import time
import psycopg2
from psycopg2.extras import DictCursor, RealDictCursor
from psycopg2.pool import ThreadedConnectionPool
from contextlib import contextmanager
from typing import Dict, List, Any, Optional, Union, Tuple, Generator
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("postgres_utils")

# Thread-local storage for connection tracking
_thread_local = threading.local()

# Global connection pool
_pg_pool = None
_pool_lock = threading.Lock()

def get_postgres_connection_params() -> Dict[str, Any]:
    """
    Get PostgreSQL connection parameters from environment variables with enhanced validation.
    
    Returns:
        Dict[str, Any]: Dictionary with connection parameters
    """
    # Get required parameters with defaults
    params = {
        "host": os.getenv("POSTGRES_SERVER", "localhost"),
        "port": int(os.getenv("POSTGRES_PORT", 5432)),
        "user": os.getenv("POSTGRES_USER", "postgres"),
        "password": os.getenv("POSTGRES_PASSWORD", ""),
        "database": os.getenv("POSTGRES_DB", "postgres"),
        "sslmode": os.getenv("POSTGRES_SSL_MODE", "prefer"),
        # Connection timeout
        "connect_timeout": int(os.getenv("POSTGRES_CONNECT_TIMEOUT", 10))
    }
    
    # Log connection parameters (without password)
    safe_params = params.copy()
    safe_params["password"] = "*****" if params["password"] else "<not set>"
    logger.debug(f"PostgreSQL connection parameters: {safe_params}")
    
    return params

def initialize_connection_pool(min_connections: int = 1, max_connections: int = 10) -> None:
    """
    Initialize the PostgreSQL connection pool.
    
    Args:
        min_connections: Minimum number of connections to keep in the pool
        max_connections: Maximum number of connections allowed in the pool
    """
    global _pg_pool
    
    with _pool_lock:
        if _pg_pool is not None:
            logger.info("Connection pool already initialized")
            return
        
        try:
            # Get connection parameters
            params = get_postgres_connection_params()
            
            # Create connection pool
            logger.info(f"Initializing PostgreSQL connection pool (min={min_connections}, max={max_connections})")
            _pg_pool = ThreadedConnectionPool(
                minconn=min_connections,
                maxconn=max_connections,
                **params
            )
            
            # Test the pool by getting and returning a connection
            conn = _pg_pool.getconn()
            _pg_pool.putconn(conn)
            
            logger.info("PostgreSQL connection pool initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize connection pool: {str(e)}")
            raise

def close_connection_pool() -> None:
    """
    Close the PostgreSQL connection pool and release all connections.
    """
    global _pg_pool
    
    with _pool_lock:
        if _pg_pool is not None:
            logger.info("Closing PostgreSQL connection pool")
            _pg_pool.closeall()
            _pg_pool = None
            logger.info("PostgreSQL connection pool closed")

@contextmanager
def get_db_connection() -> Generator[psycopg2.extensions.connection, None, None]:
    """
    Get a connection from the pool with proper error handling.
    
    Yields:
        psycopg2.extensions.connection: Database connection
    """
    global _pg_pool
    
    # Initialize pool if not already initialized
    if _pg_pool is None:
        initialize_connection_pool()
    
    # Track connections per thread to avoid leaks
    if not hasattr(_thread_local, 'conn_count'):
        _thread_local.conn_count = 0
    
    conn = None
    start_time = time.time()
    
    try:
        # Get connection from pool
        conn = _pg_pool.getconn(key=threading.get_ident())
        _thread_local.conn_count += 1
        logger.debug(f"Got connection from pool (thread: {threading.get_ident()}, count: {_thread_local.conn_count})")
        
        # Yield connection to caller
        yield conn
        
        # Commit changes if no exception occurred
        conn.commit()
    except psycopg2.Error as e:
        # Log the error with detailed information
        logger.error(f"Database error: {e.pgerror if hasattr(e, 'pgerror') else str(e)}")
        logger.error(f"Error code: {e.pgcode if hasattr(e, 'pgcode') else 'unknown'}")
        
        # Rollback transaction on error
        if conn:
            conn.rollback()
        
        # Re-raise the exception
        raise
    except Exception as e:
        # Log any other exceptions
        logger.error(f"Unexpected error: {str(e)}")
        
        # Rollback transaction on error
        if conn:
            conn.rollback()
        
        # Re-raise the exception
        raise
    finally:
        # Return connection to pool
        if conn:
            _pg_pool.putconn(conn, key=threading.get_ident())
            _thread_local.conn_count -= 1
            logger.debug(f"Returned connection to pool (thread: {threading.get_ident()}, count: {_thread_local.conn_count}, time: {time.time() - start_time:.3f}s)")

@contextmanager
def get_db_cursor(cursor_factory=None) -> Generator[psycopg2.extensions.cursor, None, None]:
    """
    Get a database cursor with proper connection handling.
    
    Args:
        cursor_factory: Optional cursor factory (e.g., DictCursor, RealDictCursor)
    
    Yields:
        psycopg2.extensions.cursor: Database cursor
    """
    with get_db_connection() as conn:
        # Create cursor with specified factory or default
        if cursor_factory:
            cursor = conn.cursor(cursor_factory=cursor_factory)
        else:
            cursor = conn.cursor()
        
        try:
            yield cursor
        finally:
            cursor.close()

def execute_query(query: str, params: tuple = None, fetch_one: bool = False, dict_cursor: bool = True) -> Union[List[Dict[str, Any]], Dict[str, Any], None]:
    """
    Execute a SQL query with proper error handling and connection management.
    
    Args:
        query: SQL query to execute
        params: Query parameters
        fetch_one: Whether to fetch one row or all rows
        dict_cursor: Whether to use a dictionary cursor
    
    Returns:
        Query results as a list of dictionaries, a single dictionary, or None
    """
    cursor_factory = RealDictCursor if dict_cursor else None
    
    with get_db_cursor(cursor_factory) as cursor:
        try:
            # Execute query with parameters
            cursor.execute(query, params)
            
            # Return results based on fetch_one flag
            if cursor.description:  # Check if query returns data
                if fetch_one:
                    return cursor.fetchone()
                else:
                    return cursor.fetchall()
            return None
        except psycopg2.Error as e:
            # Log the error with detailed information
            logger.error(f"Query execution error: {e.pgerror if hasattr(e, 'pgerror') else str(e)}")
            logger.error(f"Error code: {e.pgcode if hasattr(e, 'pgcode') else 'unknown'}")
            logger.error(f"Query: {query}")
            logger.error(f"Params: {params}")
            
            # Re-raise the exception
            raise

def execute_batch(query: str, params_list: List[tuple]) -> int:
    """
    Execute a batch SQL query with proper error handling and connection management.
    
    Args:
        query: SQL query to execute
        params_list: List of parameter tuples for batch execution
    
    Returns:
        int: Number of rows affected
    """
    with get_db_cursor() as cursor:
        try:
            # Execute batch query
            from psycopg2.extras import execute_batch as pg_execute_batch
            pg_execute_batch(cursor, query, params_list)
            return cursor.rowcount
        except psycopg2.Error as e:
            # Log the error with detailed information
            logger.error(f"Batch execution error: {e.pgerror if hasattr(e, 'pgerror') else str(e)}")
            logger.error(f"Error code: {e.pgcode if hasattr(e, 'pgcode') else 'unknown'}")
            logger.error(f"Query: {query}")
            logger.error(f"Params count: {len(params_list)}")
            
            # Re-raise the exception
            raise

def reset_sequences() -> Dict[str, int]:
    """
    Reset PostgreSQL sequences based on the maximum values in their respective tables.
    This is useful after bulk imports or when sequences get out of sync.
    
    Returns:
        Dict[str, int]: Dictionary mapping sequence names to their new values
    """
    # Query to find all sequences and their associated tables/columns
    find_sequences_query = """
    SELECT
        ns.nspname AS schema,
        seq.relname AS sequence,
        tab.relname AS table,
        attr.attname AS column
    FROM pg_class seq
    JOIN pg_namespace ns ON seq.relnamespace = ns.oid
    JOIN pg_depend dep ON seq.oid = dep.objid
    JOIN pg_class tab ON dep.refobjid = tab.oid
    JOIN pg_attribute attr ON attr.attrelid = tab.oid AND attr.attnum = dep.refobjsubid
    WHERE seq.relkind = 'S' AND ns.nspname NOT IN ('pg_catalog', 'information_schema')
    """
    
    # Get all sequences
    sequences = execute_query(find_sequences_query)
    
    if not sequences:
        logger.info("No sequences found to reset")
        return {}
    
    results = {}
    
    # For each sequence, get the max value from its table and reset the sequence
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            for seq in sequences:
                schema = seq['schema']
                sequence = seq['sequence']
                table = seq['table']
                column = seq['column']
                
                try:
                    # Get the maximum value from the table
                    cursor.execute(f"SELECT COALESCE(MAX({column}), 0) + 1 AS max_val FROM {schema}.{table}")
                    max_val = cursor.fetchone()[0]
                    
                    # Reset the sequence
                    cursor.execute(f"ALTER SEQUENCE {schema}.{sequence} RESTART WITH {max_val}")
                    
                    # Store the result
                    results[f"{schema}.{sequence}"] = max_val
                    logger.info(f"Reset sequence {schema}.{sequence} to {max_val}")
                except Exception as e:
                    logger.error(f"Error resetting sequence {schema}.{sequence}: {str(e)}")
    
    return results

def get_table_sizes() -> List[Dict[str, Any]]:
    """
    Get the sizes of all tables in the database.
    
    Returns:
        List[Dict[str, Any]]: List of dictionaries with table information
    """
    query = """
    SELECT
        schemaname AS schema,
        relname AS table,
        pg_size_pretty(pg_total_relation_size(relid)) AS total_size,
        pg_size_pretty(pg_relation_size(relid)) AS table_size,
        pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid)) AS index_size,
        pg_total_relation_size(relid) AS total_bytes
    FROM pg_catalog.pg_statio_user_tables
    ORDER BY pg_total_relation_size(relid) DESC
    """
    
    return execute_query(query)

def get_database_stats() -> Dict[str, Any]:
    """
    Get comprehensive database statistics.
    
    Returns:
        Dict[str, Any]: Dictionary with database statistics
    """
    # Get database size
    size_query = "SELECT pg_size_pretty(pg_database_size(current_database())) AS db_size"
    db_size = execute_query(size_query, fetch_one=True)
    
    # Get connection information
    conn_query = """
    SELECT 
        max_conn,
        used,
        res_for_super,
        max_conn - used - res_for_super AS available
    FROM 
        (SELECT count(*) used FROM pg_stat_activity) t1,
        (SELECT setting::int res_for_super FROM pg_settings WHERE name='superuser_reserved_connections') t2,
        (SELECT setting::int max_conn FROM pg_settings WHERE name='max_connections') t3
    """
    conn_info = execute_query(conn_query, fetch_one=True)
    
    # Get table counts
    table_count_query = """
    SELECT count(*) AS table_count
    FROM pg_catalog.pg_tables
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
    """
    table_count = execute_query(table_count_query, fetch_one=True)
    
    # Get index counts and sizes
    index_query = """
    SELECT 
        count(*) AS index_count,
        pg_size_pretty(sum(pg_relation_size(indexrelid))) AS index_size
    FROM pg_catalog.pg_indexes idx
    JOIN pg_catalog.pg_class cls ON cls.relname = idx.indexname
    WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
    """
    index_info = execute_query(index_query, fetch_one=True)
    
    # Get active queries
    active_query = """
    SELECT 
        count(*) AS active_queries,
        count(*) FILTER (WHERE state = 'active') AS running_queries,
        count(*) FILTER (WHERE state = 'idle') AS idle_connections
    FROM pg_stat_activity
    WHERE backend_type = 'client backend'
    """
    active_info = execute_query(active_query, fetch_one=True)
    
    # Combine all statistics
    stats = {
        "database_size": db_size.get('db_size') if db_size else "Unknown",
        "connections": {
            "max": conn_info.get('max_conn') if conn_info else 0,
            "used": conn_info.get('used') if conn_info else 0,
            "available": conn_info.get('available') if conn_info else 0,
            "reserved_for_superuser": conn_info.get('res_for_super') if conn_info else 0
        },
        "tables": table_count.get('table_count') if table_count else 0,
        "indexes": {
            "count": index_info.get('index_count') if index_info else 0,
            "size": index_info.get('index_size') if index_info else "Unknown"
        },
        "queries": {
            "active": active_info.get('active_queries') if active_info else 0,
            "running": active_info.get('running_queries') if active_info else 0,
            "idle": active_info.get('idle_connections') if active_info else 0
        }
    }
    
    return stats

def vacuum_analyze(table: str = None) -> bool:
    """
    Run VACUUM ANALYZE on the specified table or the entire database.
    
    Args:
        table: Optional table name to vacuum
    
    Returns:
        bool: True if successful, False otherwise
    """
    with get_db_connection() as conn:
        # Set autocommit mode for VACUUM
        old_isolation_level = conn.isolation_level
        conn.set_isolation_level(0)  # ISOLATION_LEVEL_AUTOCOMMIT
        
        try:
            with conn.cursor() as cursor:
                if table:
                    logger.info(f"Running VACUUM ANALYZE on table {table}")
                    cursor.execute(f"VACUUM ANALYZE {table}")
                else:
                    logger.info("Running VACUUM ANALYZE on all tables")
                    cursor.execute("VACUUM ANALYZE")
                return True
        except Exception as e:
            logger.error(f"Error during VACUUM ANALYZE: {str(e)}")
            return False
        finally:
            # Restore previous isolation level
            conn.set_isolation_level(old_isolation_level)

def test_postgres_connection() -> Tuple[bool, str]:
    """
    Test connection to PostgreSQL with detailed error reporting.
    
    Returns:
        Tuple[bool, str]: (success, message)
    """
    start_time = time.time()
    
    try:
        # Get connection parameters
        params = get_postgres_connection_params()
        
        # Connect to PostgreSQL
        conn = psycopg2.connect(**params)
        
        # Get database version and connection info
        cursor = conn.cursor(cursor_factory=DictCursor)
        cursor.execute("""
            SELECT version(), 
                   current_setting('max_connections') as max_connections,
                   (SELECT count(*) FROM pg_stat_activity) as current_connections
        """)
        result = cursor.fetchone()
        version = result["version"]
        max_connections = result["max_connections"]
        current_connections = result["current_connections"]
        
        # Close connection properly
        cursor.close()
        conn.close()
        
        connection_time = time.time() - start_time
        message = f"Successfully connected to PostgreSQL in {connection_time:.2f}s: {version}"
        logger.info(message)
        logger.info(f"PostgreSQL connections: {current_connections}/{max_connections}")
        
        return True, message
    except psycopg2.OperationalError as e:
        connection_time = time.time() - start_time
        message = f"PostgreSQL connection failed after {connection_time:.2f}s: {str(e)}"
        logger.error(message)
        
        # Provide more specific error messages
        error_msg = str(e).lower()
        if "timeout" in error_msg:
            message += " - Connection timeout. Check network or server load."
        elif "authentication" in error_msg:
            message += " - Authentication failed. Check credentials."
        elif "does not exist" in error_msg:
            message += " - Database does not exist. Check database name."
        elif "connection refused" in error_msg:
            message += " - Connection refused. Check if server is running and accessible."
        
        return False, message
    except Exception as e:
        connection_time = time.time() - start_time
        message = f"Unexpected error connecting to PostgreSQL after {connection_time:.2f}s: {str(e)}"
        logger.error(message)
        return False, message
