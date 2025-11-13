"""
Authentication API schemas.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field


class SignupRequest(BaseModel):
    """Signup request schema."""
    
    email: EmailStr
    password: str = Field(..., min_length=6)
    username: str = Field(..., min_length=3, max_length=50)


class LoginRequest(BaseModel):
    """Login request schema."""
    
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    """User response schema for API."""
    
    id: str
    username: str
    email: EmailStr
    phone: Optional[str] = None
    company: Optional[str] = None
    profile_complete: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    """Authentication response schema."""
    
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse
