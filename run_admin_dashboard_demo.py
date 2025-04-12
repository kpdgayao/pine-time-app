"""
Run the Pine Time Admin Dashboard in demo mode.
This script sets the DEMO_MODE environment variable to "true" before running the Streamlit app.
"""

import os
import subprocess
import sys

# Set demo mode environment variable
os.environ["DEMO_MODE"] = "true"

# Get the path to the Streamlit executable
streamlit_path = os.path.join(os.path.dirname(sys.executable), "streamlit")

# Run the Streamlit app
print("Starting Pine Time Admin Dashboard in demo mode...")
print("Use the following demo credentials:")
print("Username: demo@pinetimeexperience.com")
print("Password: demo")
print("\nNote: In demo mode, you can also use any username/password combination.")

# Run the Streamlit app
subprocess.run([streamlit_path, "run", "admin_dashboard/app.py"])
