"""
Routes package - API endpoints.
"""
from .auth import router as auth_router
from .user import router as user_router
from .reviews import router as reviews_router

__all__ = [
    "auth_router",
    "user_router",
    "reviews_router",
]
