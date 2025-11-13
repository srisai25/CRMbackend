"""
User domain models.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class UserProfile(BaseModel):
    """User profile domain model."""
    
    id: str = Field(..., description="User UUID from auth.users")
    username: str = Field(..., min_length=3, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=100)
    google_maps_url: Optional[str] = Field(None, max_length=500, description="Google Maps business URL for reviews")
    profile_complete: bool = Field(default=False)
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    """Model for creating a new user profile."""
    
    username: str = Field(..., min_length=3, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=100)
    google_maps_url: Optional[str] = Field(None, max_length=500)


class UserUpdate(BaseModel):
    """Model for updating user profile."""
    
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=100)
    google_maps_url: Optional[str] = Field(None, max_length=500)
