# Pine Time Backend Deployment

This directory contains the configuration files for deploying the Pine Time backend application to AWS Elastic Beanstalk.

## Deployment Configuration

### Environment Variables

The environment variables for the application are defined in `.ebextensions/04_environment.config`. This file contains important configuration for:

- Database connection parameters
- CORS settings
- Authentication settings
- Connection pooling parameters

### CORS Configuration

The application uses CORS to allow cross-origin requests. The CORS configuration is defined in two places:

1. **Environment Variables**: In `.ebextensions/04_environment.config`, the `BACKEND_CORS_ORIGINS` variable defines the allowed origins as a JSON array:

```yaml
BACKEND_CORS_ORIGINS: '["https://pinetimeapp.com", "https://www.pinetimeapp.com", "http://pinetimeapp.com", "http://www.pinetimeapp.com", "https://api.pinetimeapp.com", "https://pine-time-app-env-v2.eba-keu6sc2y.us-east-1.elasticbeanstalk.com", "http://pine-time-app-env-v2.eba-keu6sc2y.us-east-1.elasticbeanstalk.com", "http://localhost:5173", "http://localhost:8000", "http://localhost:8501"]'
```

2. **Application Code**: In `app/main.py`, the `all_origins` list defines a hardcoded list of allowed origins. The application merges this list with the origins from the environment variable.

When updating the CORS configuration, ensure both places are updated to maintain consistency.

## Deployment Process

1. **Create Deployment Package**:

```bash
# Create deployment directory
mkdir pine-time-deploy

# Copy .ebextensions and .platform directories
cp -r .ebextensions pine-time-deploy/
cp -r .platform pine-time-deploy/

# Copy application code
cp -r ../app pine-time-deploy/

# Copy Procfile and requirements.txt
cp Procfile pine-time-deploy/
cp ../requirements.txt pine-time-deploy/

# Create ZIP file
cd pine-time-deploy
zip -r ../pine-time-deploy.zip .
cd ..
```

2. **Deploy to Elastic Beanstalk**:

   - Log in to the AWS Elastic Beanstalk console
   - Navigate to your Pine Time application environment
   - Upload the `pine-time-deploy.zip` file as a new application version

3. **Verify Deployment**:

   - Check the Elastic Beanstalk logs for any errors
   - Test the API endpoints to ensure they're working correctly
   - Verify CORS headers in API responses

## Troubleshooting

### CORS Issues

If you encounter CORS issues:

1. Check the application logs for messages about CORS origins
2. Verify that both CORS configurations include all necessary domains
3. Test API endpoints directly using tools like curl or Postman to isolate frontend vs. backend issues
4. Clear browser cache to ensure you're not seeing cached responses with incorrect CORS headers

### Database Connectivity

If you encounter database connectivity issues:

1. Verify that all PostgreSQL environment variables are correctly set
2. Check that the `POSTGRES_SSL_MODE` is set to `require` for Neon PostgreSQL
3. Test the database connection directly using the `test_db_connection.py` script
