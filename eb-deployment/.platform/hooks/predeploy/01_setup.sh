#!/bin/bash

# Make sure we're in the project directory
cd /var/app/staging/

# Log the deployment information
echo "Starting deployment $(date)" >> /var/log/deploy.log
echo "Python path: $(which python)" >> /var/log/deploy.log
echo "Python version: $(python --version)" >> /var/log/deploy.log

# Install requirements
pip install -r requirements.txt

# Log completion
echo "Finished setup $(date)" >> /var/log/deploy.log
