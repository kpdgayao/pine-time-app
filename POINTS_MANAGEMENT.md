# Pine Time Points Management Utilities

## Overview

This document explains the points management utilities available in the Pine Time application for maintaining and troubleshooting the gamification system in production.

## Available Utilities

The application includes several command-line utilities for managing the points system, located in the `app/utils/` directory:

### 1. manage_points.py

A comprehensive utility for managing points transactions with multiple functions:

```bash
# Display current points data
python app/utils/manage_points.py --display

# Reset points data with sample data
python app/utils/manage_points.py --reset

# Clean all points transactions
python app/utils/manage_points.py --clean

# Show points summary by user
python app/utils/manage_points.py --summary
```

### 2. clean_points_transactions.py

Utility for cleaning up invalid or corrupted points transactions:

```bash
python app/utils/clean_points_transactions.py
```

### 3. reset_points_data.py

Resets the points data to a known good state with sample data:

```bash
python app/utils/reset_points_data.py
```

### 4. reset_points_clean.py

Completely removes all points transactions from the database:

```bash
python app/utils/reset_points_clean.py
```

### 5. view_points_transactions.py

Displays detailed information about points transactions:

```bash
python app/utils/view_points_transactions.py
```

### 6. run_points_reset.py

Orchestrates a full reset of the points system:

```bash
python app/utils/run_points_reset.py
```

## Common Production Tasks

### Viewing Points Summary

To get a quick overview of points by user:

```bash
python app/utils/manage_points.py --summary
```

### Troubleshooting Points Issues

If users report missing points or incorrect balances:

1. Check the points transactions:
   ```bash
   python app/utils/view_points_transactions.py
   ```

2. Look for any anomalies in the data

3. If necessary, clean up corrupted transactions:
   ```bash
   python app/utils/clean_points_transactions.py
   ```

### Resetting the Points System

In case of major issues requiring a full reset:

1. Back up the current data (if needed)
2. Run the reset script:
   ```bash
   python app/utils/run_points_reset.py
   ```

## Integration with PostgreSQL

All utilities are designed to work with the PostgreSQL database and include:

- Proper connection pooling
- Error handling for database constraints
- Transaction management
- Logging of all operations

## Security Considerations

- These utilities should only be run by administrators
- They require database access credentials
- Production usage should be logged and monitored
- Consider backing up data before running destructive operations

## Logging

All operations are logged to:

- Console output
- Application log file (`logs/app.log`)

## Extending the Utilities

To add new functionality:

1. Create a new utility script in the `app/utils/` directory
2. Follow the pattern of existing utilities
3. Include proper error handling and logging
4. Document the new utility in this guide
