"""Main API v1 router."""

from fastapi import APIRouter

from src.api.v1.endpoints import health

# Create main v1 router
api_router = APIRouter()

# Include endpoint routers
api_router.include_router(health.router, tags=["Health"])

# You can add more routers here
# api_router.include_router(users.router, prefix="/users", tags=["Users"])
# api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
