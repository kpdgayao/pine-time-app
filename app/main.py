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

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

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