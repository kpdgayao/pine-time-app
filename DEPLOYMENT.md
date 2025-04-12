# Pine Time Application Deployment Guide

This guide provides instructions for deploying the Pine Time application using Docker.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Deployment Steps

### 1. Configure Environment Variables

Before deploying, make sure to update the environment variables in the `docker-compose.yml` file:

```yaml
environment:
  - DATABASE_URL=postgresql://postgres:postgres@db:5432/pine_time
  - BACKEND_CORS_ORIGINS=["http://localhost:8501", "http://localhost:8000"]
  - SECRET_KEY=your_secret_key_here_please_change_in_production
  - ALGORITHM=HS256
  - ACCESS_TOKEN_EXPIRE_MINUTES=30
```

For production, you should:
- Change the `SECRET_KEY` to a secure random string
- Update `BACKEND_CORS_ORIGINS` to include your production domain
- Consider using environment-specific configuration files

### 2. Build and Start the Application

Run the following command in the project root directory:

```bash
docker-compose up -d
```

This will:
- Build the Docker image for the application
- Start the PostgreSQL database
- Start the FastAPI backend on port 8000
- Start the Streamlit frontend on port 8501

### 3. Initialize the Database

If this is the first time running the application, you may need to initialize the database:

```bash
docker-compose exec web python init_sqlite_db.py
```

Or for PostgreSQL:

```bash
docker-compose exec web python reset_postgres_sequences.py
```

### 4. Access the Application

- FastAPI Backend: http://localhost:8000
- Streamlit Frontend: http://localhost:8501
- API Documentation: http://localhost:8000/docs

## Cloud Deployment Options

### Deploying to Heroku

1. Install the Heroku CLI
2. Create a Heroku app:
   ```bash
   heroku create pine-time-app
   ```
3. Add PostgreSQL add-on:
   ```bash
   heroku addons:create heroku-postgresql:hobby-dev
   ```
4. Push to Heroku:
   ```bash
   git push heroku main
   ```

### Deploying to AWS

1. Create an ECR repository for your Docker image
2. Push your Docker image to ECR
3. Deploy using ECS or EKS
4. Set up an RDS PostgreSQL instance
5. Configure environment variables in your ECS task definition

### Deploying to Google Cloud

1. Create a project in Google Cloud
2. Enable Cloud Run and Cloud SQL
3. Build and push your Docker image to Google Container Registry
4. Deploy to Cloud Run with connection to Cloud SQL

## Monitoring and Maintenance

- Check logs: `docker-compose logs -f`
- Restart services: `docker-compose restart`
- Stop all services: `docker-compose down`
- Update and rebuild: `docker-compose up -d --build`

## Troubleshooting

- If the frontend can't connect to the backend, check the CORS settings
- For database connection issues, verify the DATABASE_URL environment variable
- Check the logs for specific error messages: `docker-compose logs -f web`
