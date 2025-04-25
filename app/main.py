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
from fastapi.staticfiles import StaticFiles
import pathlib
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
# Define default origins to always include
default_origins = [
    "http://localhost",
    "http://localhost:5173", 
    "http://localhost:3000",
    "http://localhost:8000",
    "http://localhost:8501",
    "https://master.dq3hhwbwgg2a3.amplifyapp.com",
    "http://pine-time-app-env-v2.eba-keu6sc2y.us-east-1.elasticbeanstalk.com"
]

# Parse CORS origins from environment variable (should be a JSON array)
origins_str = os.getenv(
    "BACKEND_CORS_ORIGINS",
    '["https://master.dq3hhwbwgg2a3.amplifyapp.com","http://pine-time-app-env-v2.eba-keu6sc2y.us-east-1.elasticbeanstalk.com","http://localhost:5173","http://localhost:3000"]'
)

try:
    # Parse as JSON array
    origins = json.loads(origins_str)
    # Add default origins
    for origin in default_origins:
        if origin not in origins:
            origins.append(origin)
    logging.info(f"CORS origins loaded: {origins}")
except json.JSONDecodeError as e:
    # Fallback in case JSON parsing fails
    logging.error(f"Failed to parse CORS origins as JSON: {origins_str}. Error: {str(e)}")
    # Use default origins as fallback
    origins = default_origins
    logging.info(f"CORS origins (fallback method): {origins}")

# Hard-coded CORS origins for local/dev/prod
CORS_ORIGINS = [
    "http://localhost",
    "http://localhost:5173",
    "http://localhost:3000",
    "http://localhost:8000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8000",
    "https://master.dq3hhwbwgg2a3.amplifyapp.com",
    "http://pine-time-app-env-v2.eba-keu6sc2y.us-east-1.elasticbeanstalk.com"
]

# Note: When allow_credentials=True, allow_origins cannot be ['*']
# We need to specify exact origins

# Define all possible origins to support
all_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "https://master.dq3hhwbwgg2a3.amplifyapp.com",
    "http://pine-time-app-env-v2.eba-keu6sc2y.us-east-1.elasticbeanstalk.com"
]

# Create a middleware to handle CORS with proper error handling
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
import logging

class CustomCORSMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Get the origin from the request headers
        origin = request.headers.get("origin", "")
        
        # Log the incoming request for debugging
        logging.info(f"Incoming request from origin: {origin}")
        
        # Handle preflight OPTIONS requests specially
        if request.method == "OPTIONS":
            # Create a response with appropriate CORS headers
            response = Response()
            if origin in all_origins:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD"
                response.headers["Access-Control-Allow-Headers"] = "*"
                response.headers["Access-Control-Max-Age"] = "600"
            return response
        
        # For non-OPTIONS requests, proceed with normal processing
        try:
            response = await call_next(request)
            
            # Add CORS headers to the response
            if origin in all_origins:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
                
            return response
        except Exception as e:
            logging.error(f"Error processing request: {str(e)}")
            # Create a response for the error case
            response = Response(status_code=500)
            if origin in all_origins:
                response.headers["Access-Control-Allow-Origin"] = origin
                response.headers["Access-Control-Allow-Credentials"] = "true"
            return response

# Add the custom CORS middleware
app.add_middleware(CustomCORSMiddleware)

# Also keep the standard CORS middleware for compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=all_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
    allow_headers=["*"],  # Allow all headers for simplicity
    expose_headers=["Content-Length", "Content-Type", "Authorization"],
    max_age=600  # Cache preflight requests for 10 minutes
)

# --- End CORS Configuration ---

# Set up static file serving for placeholder images and other assets
static_dir = pathlib.Path(__file__).parent / "static"
if not static_dir.exists():
    static_dir.mkdir(parents=True, exist_ok=True)
    # Create placeholder directories
    placeholder_dir = static_dir / "images" / "placeholders" / "events"
    placeholder_dir.mkdir(parents=True, exist_ok=True)
    # Create default placeholder file
    default_event = placeholder_dir / "default-event.jpg"
    if not default_event.exists():
        with open(default_event, "w") as f:
            f.write("Placeholder image")
    logging.info(f"Created static file directory and placeholders at {static_dir}")
else:
    logging.info(f"Using existing static file directory at {static_dir}")

# Mount the static directory to serve files
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

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


@app.get("/health", include_in_schema=False)
async def health_check() -> dict:
    """
    Health check endpoint that verifies database connectivity.
    Returns status and database connection status.
    Not included in OpenAPI schema.
    """
    import logging
    from sqlalchemy.exc import SQLAlchemyError

    try:
        # Attempt to connect and execute a simple query
        from sqlalchemy import text
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except SQLAlchemyError as e:
        logging.error(f"Health check DB error: {e}")
        return {"status": "unhealthy", "database": str(e)}
    except Exception as e:
        logging.error(f"Health check unknown error: {e}")
        return {"status": "unhealthy", "database": str(e)}