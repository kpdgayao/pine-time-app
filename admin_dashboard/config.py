"""
Configuration settings for the Pine Time User Interface.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
API_V1_STR = "/api/v1"  # Match the FastAPI prefix
API_ENDPOINTS = {
    "auth": {
        "token": f"{API_BASE_URL}{API_V1_STR}/login/access-token",
        "refresh": f"{API_BASE_URL}{API_V1_STR}/login/refresh-token",
        "verify": f"{API_BASE_URL}{API_V1_STR}/login/test-token",
        "register": f"{API_BASE_URL}{API_V1_STR}/users",  # Registration is likely under users
        "login": f"{API_BASE_URL}{API_V1_STR}/login/access-token",  # Add login endpoint
    },
    "users": {
        "list": f"{API_BASE_URL}{API_V1_STR}/users",
        "detail": f"{API_BASE_URL}{API_V1_STR}/users/{{user_id}}",
        "update": f"{API_BASE_URL}{API_V1_STR}/users/{{user_id}}",
        "points": f"{API_BASE_URL}{API_V1_STR}/users/{{user_id}}/points",
        "badges": f"{API_BASE_URL}{API_V1_STR}/users/{{user_id}}/badges",
        "events": f"{API_BASE_URL}{API_V1_STR}/users/{{user_id}}/events",
        "profile": f"{API_BASE_URL}{API_V1_STR}/users/me",
        "register": f"{API_BASE_URL}{API_V1_STR}/users/register",
    },
    "events": {
        "list": f"{API_BASE_URL}{API_V1_STR}/events",
        "detail": f"{API_BASE_URL}{API_V1_STR}/events/{{event_id}}",
        "create": f"{API_BASE_URL}{API_V1_STR}/events",
        "update": f"{API_BASE_URL}{API_V1_STR}/events/{{event_id}}",
        "delete": f"{API_BASE_URL}{API_V1_STR}/events/{{event_id}}",
        "check_in": f"{API_BASE_URL}{API_V1_STR}/events/{{event_id}}/check-in",
        "complete": f"{API_BASE_URL}{API_V1_STR}/events/{{event_id}}/complete",
        "register": f"{API_BASE_URL}{API_V1_STR}/events/{{event_id}}/register",
    },
    "analytics": {
        "event_popularity": f"{API_BASE_URL}{API_V1_STR}/analytics/events/popularity",
        "user_engagement": f"{API_BASE_URL}{API_V1_STR}/analytics/users/engagement",
        "points_distribution": f"{API_BASE_URL}{API_V1_STR}/analytics/points/distribution",
    },
    "points": {
        "leaderboard": f"{API_BASE_URL}{API_V1_STR}/points/leaderboard",
        "history": f"{API_BASE_URL}{API_V1_STR}/points/history",
    },
    "badges": {
        "list": f"{API_BASE_URL}{API_V1_STR}/badges",
        "detail": f"{API_BASE_URL}{API_V1_STR}/badges/{{badge_id}}",
        "categories": f"{API_BASE_URL}{API_V1_STR}/badges/categories",
    },
    "registrations": {
        "create": f"{API_BASE_URL}{API_V1_STR}/registrations",
        "list": f"{API_BASE_URL}{API_V1_STR}/registrations",
        "detail": f"{API_BASE_URL}{API_V1_STR}/registrations/{{registration_id}}",
        "delete": f"{API_BASE_URL}{API_V1_STR}/registrations/{{registration_id}}",
    }
}

# UI Configuration
PAGE_TITLE = "Pine Time Experience Baguio"
PAGE_ICON = "🌲"
THEME_COLOR = "#2E7D32"  # Forest green theme

# Authentication Settings
SESSION_EXPIRY = int(os.getenv("SESSION_EXPIRY", "3600"))  # Session expiry in seconds (1 hour)
TOKEN_REFRESH_MARGIN = int(os.getenv("TOKEN_REFRESH_MARGIN", "300"))  # Refresh token if less than 5 minutes remaining

# API Request Settings
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "10"))  # Request timeout in seconds
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))  # Maximum number of retries for failed requests
RETRY_BACKOFF = float(os.getenv("RETRY_BACKOFF", "0.5"))  # Backoff factor for retries

# Pagination Settings
DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", "20"))  # Default number of items per page

# Database Settings
DATABASE_TYPE = os.getenv("DATABASE_TYPE", "sqlite").lower()
SQLITE_DATABASE_URI = os.getenv("SQLITE_DATABASE_URI", "sqlite:///./pine_time.db")

# PostgreSQL Settings
POSTGRES_SERVER = os.getenv("POSTGRES_SERVER", "localhost")
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "")
POSTGRES_DB = os.getenv("POSTGRES_DB", "pine_time")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_SSL_MODE = os.getenv("POSTGRES_SSL_MODE", "prefer")

# Connection Pool Settings
POOL_SIZE = int(os.getenv("POOL_SIZE", "5"))
MAX_OVERFLOW = int(os.getenv("MAX_OVERFLOW", "10"))
POOL_TIMEOUT = int(os.getenv("POOL_TIMEOUT", "30"))
POOL_RECYCLE = int(os.getenv("POOL_RECYCLE", "1800"))

# Demo Mode Settings
DEMO_MODE = os.getenv("DEMO_MODE", "false").lower() == "true"

# Get database URI based on configuration
def get_database_uri():
    """Get database URI based on configuration"""
    if DATABASE_TYPE == "postgresql":
        return f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_SERVER}:{POSTGRES_PORT}/{POSTGRES_DB}"
    else:
        return SQLITE_DATABASE_URI