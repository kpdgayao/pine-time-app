from fastapi import APIRouter

from app.api.endpoints import login, users, events, registrations, badges, points, auth, badges_admin, admin_points, registrations_admin, payment

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(events.router, prefix="/events", tags=["events"])
api_router.include_router(registrations.router, prefix="/registrations", tags=["registrations"])
api_router.include_router(registrations_admin.router, prefix="/registrations", tags=["registrations-admin"])
api_router.include_router(badges.router, prefix="/badges", tags=["badges"])
api_router.include_router(points.router, prefix="/points", tags=["points"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(badges_admin.router, prefix="/badges_admin", tags=["badges_admin"])
api_router.include_router(admin_points.router, prefix="/admin", tags=["admin-points"])
api_router.include_router(payment.router, prefix="/payments", tags=["payments"])