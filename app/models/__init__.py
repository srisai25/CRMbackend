"""
Models package - Domain models.
"""
from .user import UserProfile, UserCreate, UserUpdate
from .review import Review, ReviewCreate, ScrapeRequest, ScrapeResponse

__all__ = [
    "UserProfile",
    "UserCreate", 
    "UserUpdate",
    "Review",
    "ReviewCreate",
    "ScrapeRequest",
    "ScrapeResponse",
]
