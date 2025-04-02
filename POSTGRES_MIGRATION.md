# PostgreSQL Migration Guide for Pine Time Experience Baguio

This guide provides step-by-step instructions for migrating the Pine Time Experience Baguio application from SQLite to Neon PostgreSQL while maintaining backward compatibility.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Setting Up Neon PostgreSQL](#setting-up-neon-postgresql)
3. [Environment Configuration](#environment-configuration)
4. [Migration Process](#migration-process)
5. [Verifying Migration](#verifying-migration)
6. [Troubleshooting](#troubleshooting)
7. [Production Considerations](#production-considerations)
8. [Rollback Procedure](#rollback-procedure)

## Prerequisites

Before starting the migration, ensure you have:

- Python 3.8+ installed
- Access to your Neon PostgreSQL account
- `psycopg2` or `psycopg2-binary` package installed (required for PostgreSQL connections)

Install the required PostgreSQL adapter:

```bash
pip install psycopg2-binary
```

Add this dependency to your `requirements.txt` file:

```text
psycopg2-binary==2.9.9
```

## Setting Up Neon PostgreSQL

1. **Create a Neon Account**:
   - Sign up at [https://neon.tech](https://neon.tech)
   - Create a new project for Pine Time Experience

2. **Create a Database**:
   - In your Neon dashboard, create a new database named `pine_time`
   - Note the connection details provided by Neon:
     - Host/Server name
     - Port (usually 5432)
     - Username
     - Password
     - Database name

3. **Connection String Format**:
   - The PostgreSQL connection string follows this format:

   ```text
   postgresql://username:password@hostname:port/database
   ```

## Environment Configuration

The application has been updated to support both SQLite and PostgreSQL databases through environment variables.

1. **Create a `.env` file** in the root directory of your project:

```env
# Database Configuration
DATABASE_TYPE=postgresql  # Use 'sqlite' for SQLite

# SQLite Configuration (used when DATABASE_TYPE=sqlite)
SQLITE_DATABASE_URI=sqlite:///./pine_time.db

# PostgreSQL Configuration (used when DATABASE_TYPE=postgresql)
POSTGRES_SERVER=your-neon-hostname.neon.tech
POSTGRES_USER=your-neon-username
POSTGRES_PASSWORD=your-neon-password
POSTGRES_DB=pine_time
POSTGRES_PORT=5432

# Connection Pool Settings
POOL_SIZE=5
MAX_OVERFLOW=10
POOL_TIMEOUT=30
POOL_RECYCLE=1800
```

2. **For Development**:
   - You can switch between SQLite and PostgreSQL by changing the `DATABASE_TYPE` variable
   - This allows for easy local development with SQLite while using PostgreSQL in production

## Migration Process

The migration process involves transferring all data from your SQLite database to PostgreSQL.

### Step 1: Backup Your SQLite Database

Always create a backup of your SQLite database before migration:

```bash
cp pine_time.db pine_time_backup.db
```

### Step 2: Run the Migration Script

The migration script will:

- Connect to both databases
- Create all tables in PostgreSQL
- Transfer all data while preserving relationships
- Verify data integrity (optional)

```bash
# Basic migration
python app/migrate_data.py

# With additional options
python app/migrate_data.py --batch-size 200 --verify
```

Available options:

- `--source`: Source database URI (SQLite) - defaults to `sqlite:///./pine_time.db`
- `--target`: Target database URI (PostgreSQL) - defaults to the URI from environment variables
- `--batch-size`: Number of records to transfer in each batch (default: 100)
- `--verify`: Verify data integrity after migration
- `--drop-target`: Drop all tables in target database before migration (use with caution!)

### Step 3: Test the Connection

After migration, test the database connection to ensure everything is working correctly:

```bash
# Test PostgreSQL connection
python app/test_db_connection.py --db-type postgresql

# Test SQLite connection
python app/test_db_connection.py --db-type sqlite
```

### Step 4: Update Environment Variables

Once you've verified the migration was successful, update your environment to use PostgreSQL:

```env
DATABASE_TYPE=postgresql
```

## Verifying Migration

To ensure the migration was successful, check the following:

1. **Record Counts**:
   - The migration script will report the number of records transferred for each table
   - Verify that the counts match between SQLite and PostgreSQL

2. **Data Integrity**:
   - Use the `--verify` option with the migration script to check data integrity
   - This compares record counts between the two databases

3. **Application Functionality**:
   - Run the application with PostgreSQL to ensure all features work correctly
   - Test critical paths like user registration, event creation, and point transactions

## Troubleshooting

### Connection Issues

**Problem**: Unable to connect to Neon PostgreSQL

**Solution**:

- Verify your connection details in the `.env` file
- Ensure your IP address is allowed in Neon's connection settings
- Check if your network allows outbound connections on port 5432

### Migration Errors

**Problem**: Migration script fails with SQLAlchemy errors

**Solution**:

- Check the migration logs for specific error messages
- Ensure you have the latest version of SQLAlchemy and psycopg2-binary
- For data type issues, you may need to modify the models to use PostgreSQL-compatible types

### Performance Issues

**Problem**: Slow performance with PostgreSQL compared to SQLite

**Solution**:

- Adjust connection pool settings in the `.env` file
- Add indexes to frequently queried columns
- Consider using PostgreSQL-specific optimizations like partial indexes

## Production Considerations

### Connection Pooling

The application is configured with connection pooling for PostgreSQL:

- `POOL_SIZE`: Number of connections to keep open (default: 5)
- `MAX_OVERFLOW`: Maximum number of connections to create beyond pool size (default: 10)
- `POOL_TIMEOUT`: Seconds to wait for a connection from the pool (default: 30)
- `POOL_RECYCLE`: Seconds after which a connection is recycled (default: 1800)

Adjust these values based on your application's needs and server resources.

### SSL Connections

For secure connections to Neon PostgreSQL, update your connection string to include SSL parameters:

```text
postgresql://username:password@hostname:port/database?sslmode=require
```

### Environment Variables in Production

In production environments, set environment variables securely according to your hosting platform's recommendations:

- Heroku: Use config vars
- Docker: Use environment variables in your Docker Compose file
- AWS: Use Parameter Store or Secrets Manager

## Rollback Procedure

If you encounter issues with PostgreSQL and need to roll back to SQLite:

1. **Update Environment Variables**:

   ```env
   DATABASE_TYPE=sqlite
   ```

2. **Restart the Application**:
   The application will automatically use SQLite with the existing database file.

3. **Verify Functionality**:

   ```bash
   python app/test_db_connection.py --db-type sqlite
   ```

## PostgreSQL-Specific Optimizations

The migration has implemented several PostgreSQL-specific optimizations:

1. **Connection Pooling**: Efficient reuse of database connections
2. **Connection Pre-Ping**: Verifies connections before using them from the pool
3. **Connection Recycling**: Prevents stale connections

Additional optimizations you might consider:

1. **Indexing**: Add indexes for frequently queried columns
2. **Partial Indexes**: Create indexes that cover only a subset of rows
3. **JSONB**: Use JSONB fields for flexible schema requirements
4. **Full-Text Search**: Implement PostgreSQL's powerful full-text search capabilities

---

For any questions or issues with the migration process, please refer to the troubleshooting section or contact the development team.
