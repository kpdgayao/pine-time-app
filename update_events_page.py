"""
Update the events page with the fixed version that matches the API field names.
This script backs up the original file and replaces it with the fixed version.
"""

import os
import shutil
import datetime

# Paths
admin_dashboard_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "admin_dashboard")
pages_dir = os.path.join(admin_dashboard_dir, "pages")
original_file = os.path.join(pages_dir, "events.py")
fixed_file = os.path.join(pages_dir, "events_fixed.py")
backup_file = os.path.join(pages_dir, f"events_backup_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.py")

# Create backup of original file
if os.path.exists(original_file):
    print(f"Creating backup of original events.py at {backup_file}")
    shutil.copy2(original_file, backup_file)
    
    # Replace original with fixed version
    print(f"Replacing events.py with fixed version")
    shutil.copy2(fixed_file, original_file)
    
    # Remove the fixed file
    os.remove(fixed_file)
    
    print("Update completed successfully!")
    print("You can now run the admin dashboard with the fixed events page.")
    print("To run the admin dashboard, use: streamlit run admin_dashboard/app.py")
else:
    print(f"Error: Original file {original_file} not found")
