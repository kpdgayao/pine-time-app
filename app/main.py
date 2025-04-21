import logging
from logging.handlers import RotatingFileHandler
import os
import json

# Ensure logs directory exists
os.makedirs("logs", exist_ok=True)

# Set up rotating file handler
file_handler = RotatingFileHandler(
    "logs/app.log", maxBytes=2_000_000, backupCount=5, encoding="utf-8"
)
file_handler.setLevel(logging.INFO)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s"
))

# Get root logger and add handler
root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(file_handler)

# Optional: also log to console (default in uvicorn, but explicit here)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(
    "%(asctime)s %(levelname)s %(name)s %(message)s"
))
root_logger.addHandler(console_handler)

logging.getLogger("event_registrations_debug").setLevel(logging.INFO)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.api.api import api_router
from app.api.endpoints import badges_admin, admin_points
from app.core.config import settings
from app.db.session import engine
from app.db.base import Base

# Create all tables in the database
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# --- CORS Configuration for Amplify/Elastic Beanstalk ---
# Parse CORS origins from environment variable (should be a JSON array)
origins_str = os.getenv(
    "BACKEND_CORS_ORIGINS",
    '["https://master.dq3hhwbwgg2a3.amplifyapp.com/","http://pine-time-app-env-v2.eba-keu6sc2y.us-east-1.elasticbeanstalk.com","http://localhost:5173","http://localhost:3000"]'
)

try:
    # Parse as JSON array
    origins = json.loads(origins_str)
    logging.info(f"CORS origins loaded: {origins}")
except json.JSONDecodeError as e:
    # Fallback in case JSON parsing fails
    logging.error(f"Failed to parse CORS origins as JSON: {origins_str}. Error: {str(e)}")
    # Split by comma as fallback
    origins = [origin.strip() for origin in origins_str.split(",")]
    logging.info(f"CORS origins (fallback method): {origins}")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# --- End CORS Configuration ---

app.include_router(api_router, prefix=settings.API_V1_STR)

# Register admin badge management endpoints
app.include_router(
    badges_admin.router,
    prefix="/admin/badges",
    tags=["admin-badges"]
)



@app.get("/")
def root():
    return {"message": "Welcome to Pine Time Experience Baguio API"}