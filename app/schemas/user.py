"""
User API schemas.
"""
from typing import Optional
from pydantic import BaseModel, Field


class UserUpdateRequest(BaseModel):
    """User update request schema."""
    
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    phone: Optional[str] = Field(None, max_length=20)
    company: Optional[str] = Field(None, max_length=100)
