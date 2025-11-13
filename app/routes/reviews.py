"""
Reviews routes.
"""
import logging
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status

from ..database import get_db
from ..models import UserProfile, ScrapeRequest, ScrapeResponse, Review
from ..services.review_service import ReviewService
from ..exceptions import ValidationError
from .user import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reviews", tags=["Reviews"])


@router.post("/scrape", response_model=ScrapeResponse)
async def scrape_reviews(
    request: ScrapeRequest,
    current_user: UserProfile = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Scrape reviews from Google Maps using Apify.
    
    - **url**: Google Maps business URL
    - **max_reviews**: Maximum number of reviews to scrape (default: 50, max: 200)
    
    Returns:
        ScrapeResponse with scraped reviews
    """
    try:
        review_service = ReviewService(db)
        result = await review_service.scrape_reviews(current_user.id, request, db)
        
        logger.info(f"Review scraping completed for user {current_user.id}: {result.reviews_count} reviews")
        return result
        
    except ValidationError as e:
        logger.error(f"Review scraping validation error for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Review scraping failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Review scraping failed. Please try again or contact support."
        )


@router.get("/", response_model=List[Review])
async def get_reviews(
    current_user: UserProfile = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Get all reviews for the current user.
    
    Returns:
        List of user's scraped reviews
    """
    try:
        review_service = ReviewService(db)
        reviews = await review_service.get_user_reviews(current_user.id)
        
        logger.info(f"Retrieved {len(reviews)} reviews for user {current_user.id}")
        return reviews
        
    except Exception as e:
        logger.error(f"Failed to get reviews for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve reviews. Please try again."
        )
