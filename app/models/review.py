"""
Review domain models.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Review(BaseModel):
    """Review domain model."""
    
    id: Optional[int] = Field(None, description="Auto-generated review ID")
    user_id: str = Field(..., description="User UUID who owns this review")
    author: str = Field(..., max_length=255, description="Review author name")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5 stars")
    text: Optional[str] = Field(None, description="Review text content")
    date: Optional[datetime] = Field(None, description="Review publish date")
    source_url: Optional[str] = Field(None, max_length=500, description="Source Google Maps URL")
    created_at: Optional[datetime] = Field(None, description="When review was scraped")
    
    class Config:
        from_attributes = True


class ReviewCreate(BaseModel):
    """Model for creating a new review."""
    
    author: str = Field(..., max_length=255)
    rating: int = Field(..., ge=1, le=5)
    text: Optional[str] = Field(None)
    date: Optional[datetime] = Field(None)
    source_url: Optional[str] = Field(None, max_length=500)


class ScrapeRequest(BaseModel):
    """Model for review scraping request."""
    
    url: str = Field(..., max_length=500, description="Google Maps business URL")
    max_reviews: Optional[int] = Field(50, ge=1, le=200, description="Maximum number of reviews to scrape")


class ScrapeResponse(BaseModel):
    """Model for review scraping response."""
    
    success: bool = Field(..., description="Whether scraping was successful")
    message: str = Field(..., description="Status message")
    reviews_count: int = Field(..., description="Number of reviews scraped")
    reviews: list[Review] = Field(..., description="List of scraped reviews")
