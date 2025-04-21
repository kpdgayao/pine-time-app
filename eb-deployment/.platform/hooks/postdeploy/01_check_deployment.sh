#!/bin/bash

# Log deployment information
echo "========== Pine Time Deployment Info ==========" >> /var/log/web.stdout.log
echo "Deployment completed at $(date)" >> /var/log/web.stdout.log
echo "Python version: $(python --version)" >> /var/log/web.stdout.log
echo "Pip version: $(pip --version)" >> /var/log/web.stdout.log
echo "Directory structure:" >> /var/log/web.stdout.log
ls -la /var/app/ >> /var/log/web.stdout.log
echo "===============================================" >> /var/log/web.stdout.log
