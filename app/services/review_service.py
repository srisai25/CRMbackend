"""
Review service - Business logic for review operations and Apify integration.
"""
import logging
import os
from datetime import datetime
from typing import List, Dict, Any

from ..models import Review, ReviewCreate, ScrapeRequest, ScrapeResponse
from ..exceptions import ValidationError, NotFoundError

# Try to import apify_client, make it optional
try:
    from apify_client import ApifyClient
    APIFY_AVAILABLE = True
except ImportError:
    ApifyClient = None
    APIFY_AVAILABLE = False

logger = logging.getLogger(__name__)


class ReviewService:
    """Handles review scraping and management business logic."""
    
    def __init__(self, db_client=None):
        self.db = db_client
        
        # Check if Apify is available
        if not APIFY_AVAILABLE:
            logger.warning("apify_client not available. Install with: pip install apify-client==1.7.1")
            self.apify_client = None
            return
        
        # Initialize Apify client
        self.apify_token = os.getenv("APIFY_API_TOKEN", "apify_api_oLQF0YMZCa8CTOnL9Y40x6tIASOmu23AyZ5y")
        if not self.apify_token:
            raise ValidationError("APIFY_API_TOKEN environment variable is required")
        
        self.apify_client = ApifyClient(self.apify_token)
    
    def validate_google_maps_url(self, url: str) -> bool:
        """Validate if the URL is a valid Google Maps URL."""
        valid_domains = [
            "maps.google.com",
            "www.google.com/maps",
            "google.com/maps"
        ]
        
        return any(domain in url.lower() for domain in valid_domains)
    
    async def scrape_reviews(self, user_id: str, request: ScrapeRequest, db_session=None) -> ScrapeResponse:
        """
        Scrape reviews from Google Maps using Apify.
        
        Args:
            user_id: User UUID
            request: Scraping request with URL and options
            
        Returns:
            ScrapeResponse with scraped reviews
            
        Raises:
            ValidationError: If URL is invalid or scraping fails
        """
        try:
            # Check if Apify client is available
            if not self.apify_client:
                raise ValidationError("Apify client not available. Please install apify-client: pip install apify-client==1.7.1")
            # Validate URL
            if not self.validate_google_maps_url(request.url):
                raise ValidationError("Invalid Google Maps URL. Please provide a valid Google Maps business URL.")
            
            # Prepare Apify actor input
            run_input = {
                "startUrls": [{"url": request.url}],
                "maxReviews": request.max_reviews or 50,
                "language": "en",
            }
            
            logger.info(f"Starting Apify scraping for user {user_id} with URL: {request.url}")
            
            # Get user's username for fallback author name
            user_username = "Anonymous"
            if db_session:
                from ..models.db_models import User
                user = db_session.query(User).filter(User.id == user_id).first()
                if user:
                    user_username = user.username
            
            # Run the Apify actor
            run = self.apify_client.actor("compass/google-maps-reviews-scraper").call(run_input=run_input)
            
            dataset_id = run.get("defaultDatasetId")
            if not dataset_id:
                raise ValidationError("Apify scraping failed - no dataset returned")
            
            # Fetch results from dataset
            reviews = []
            for item in self.apify_client.dataset(dataset_id).iterate_items():
                try:
                    # Parse the review data
                    review_data = ReviewCreate(
                        author=item.get('authorName') or item.get('name') or user_username,
                        rating=int(item.get('stars', 0)),
                        text=item.get('text', ''),
                        date=self._parse_date(item.get('publishAt')),
                        source_url=request.url
                    )
                    
                    # Create Review object with user_id
                    review = Review(
                        user_id=user_id,
                        author=review_data.author,
                        rating=review_data.rating,
                        text=review_data.text,
                        date=review_data.date,
                        source_url=review_data.source_url,
                        created_at=datetime.utcnow()
                    )
                    
                    reviews.append(review)
                    
                except Exception as e:
                    logger.warning(f"Failed to parse review item: {e}")
                    continue
            
            # Optionally save to database (if db client is available)
            if self.db:
                await self._save_reviews_to_db(user_id, reviews)
            
            logger.info(f"Successfully scraped {len(reviews)} reviews for user {user_id}")
            
            return ScrapeResponse(
                success=True,
                message=f"Successfully scraped {len(reviews)} reviews",
                reviews_count=len(reviews),
                reviews=reviews
            )
            
        except ValidationError:
            raise
        except Exception as e:
            logger.error(f"Review scraping failed for user {user_id}: {str(e)}")
            raise ValidationError(f"Review scraping failed: {str(e)}")
    
    def _parse_date(self, date_str: str) -> datetime:
        """Parse date string from Apify response."""
        if not date_str:
            return None
        
        try:
            # Try different date formats
            for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ"]:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If no format matches, return current time
            logger.warning(f"Could not parse date: {date_str}")
            return datetime.utcnow()
            
        except Exception as e:
            logger.warning(f"Date parsing error: {e}")
            return datetime.utcnow()
    
    async def _save_reviews_to_db(self, user_id: str, reviews: List[Review]) -> None:
        """Save reviews to MySQL database."""
        if not self.db:
            logger.warning("No database connection available for saving reviews")
            return
        
        try:
            from ..models.db_models import Review as DBReview
            
            for review in reviews:
                db_review = DBReview(
                    user_id=user_id,
                    author=review.author,
                    rating=review.rating,
                    text=review.text,
                    date=review.date,
                    source_url=review.source_url
                )
                self.db.add(db_review)
            
            self.db.commit()
            logger.info(f"Successfully saved {len(reviews)} reviews to database")
            
        except Exception as e:
            logger.error(f"Failed to save reviews to database: {str(e)}")
            self.db.rollback()
            raise
    
    async def get_user_reviews(self, user_id: str) -> List[Review]:
        """
        Get all reviews for a user from MySQL database.
        
        Args:
            user_id: User UUID
            
        Returns:
            List of user's reviews
        """
        if not self.db:
            logger.warning("No database connection available for retrieving reviews")
            return []
        
        try:
            from ..models.db_models import Review as DBReview
            
            db_reviews = self.db.query(DBReview).filter(DBReview.user_id == user_id).all()
            
            reviews = []
            for db_review in db_reviews:
                reviews.append(Review(
                    id=db_review.id,
                    user_id=db_review.user_id,
                    author=db_review.author,
                    rating=db_review.rating,
                    text=db_review.text,
                    date=db_review.date,
                    source_url=db_review.source_url,
                    created_at=db_review.created_at.isoformat() if db_review.created_at else None
                ))
            
            logger.info(f"Retrieved {len(reviews)} reviews for user {user_id}")
            return reviews
            
        except Exception as e:
            logger.error(f"Failed to get reviews from database: {str(e)}")
            return []
