#!/bin/bash
echo "Deployment completed at $(date)" >> /var/log/web.stdout.log
echo "Checking environment variables:" >> /var/log/web.stdout.log
printenv | grep -v "AWS_" >> /var/log/web.stdout.log
