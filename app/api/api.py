from fastapi import APIRouter

from app.api.endpoints import login, users, events, registrations, badges, points

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(registrations.router, prefix="/registrations", tags=["registrations"])
api_router.include_router(badges.router, prefix="/badges", tags=["badges"])
api_router.include_router(points.router, prefix="/points", tags=["points"])