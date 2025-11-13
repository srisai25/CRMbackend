"""
User service - Business logic for user operations.
"""
import logging
from typing import Dict, Any
from sqlalchemy.orm import Session

from ..exceptions import NotFoundError, DuplicateError, ValidationError
from ..models import UserProfile, UserUpdate
from ..models.db_models import User, Review
from ..schemas import UserResponse
from ..auth import jwt_handler

logger = logging.getLogger(__name__)


class UserService:
    """Handles user profile business logic."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_profile(self, user_id: str) -> UserProfile:
        """
        Get user profile.
        
        Args:
            user_id: User UUID
            
        Returns:
            UserProfile
            
        Raises:
            NotFoundError: If user not found
        """
        user = self.db.query(User).filter(User.id == user_id, User.is_active == True).first()
        
        if not user:
            raise NotFoundError("User profile")
        
        return UserProfile(
            id=user.id,
            username=user.username,
            phone=user.phone,
            company=user.company,
            google_maps_url=user.google_maps_url,
            profile_complete=user.profile_complete,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
    
    def update_profile(self, user_id: str, data: UserUpdate) -> UserProfile:
        """
        Update user profile.
        
        Args:
            user_id: User UUID
            data: Update data
            
        Returns:
            Updated UserProfile
            
        Raises:
            NotFoundError: If user not found
            DuplicateError: If username already taken
            ValidationError: If no data provided
        """
        try:
            # Prepare update data
            update_dict = {
                k: v for k, v in data.dict(exclude_unset=True).items() if v is not None
            }
            
            if not update_dict:
                raise ValidationError("No update data provided")
            
            # Get user
            user = self.db.query(User).filter(User.id == user_id, User.is_active == True).first()
            if not user:
                raise NotFoundError("User profile")
            
            # Check username uniqueness
            if "username" in update_dict:
                existing = self.db.query(User).filter(
                    User.username == update_dict["username"],
                    User.id != user_id,
                    User.is_active == True
                ).first()
                
                if existing:
                    raise DuplicateError("Username")
            
            # Update user fields
            for key, value in update_dict.items():
                setattr(user, key, value)
            
            # Update profile completeness
            user.profile_complete = bool(user.username and user.phone and user.company)
            
            self.db.commit()
            self.db.refresh(user)
            
            logger.info(f"Profile updated for user {user_id}")
            
            return UserProfile(
                id=user.id,
                username=user.username,
                phone=user.phone,
                company=user.company,
                google_maps_url=user.google_maps_url,
                profile_complete=user.profile_complete,
                created_at=user.created_at,
                updated_at=user.updated_at
            )
            
        except (DuplicateError, ValidationError, NotFoundError):
            raise
        except Exception as e:
            logger.error(f"Profile update failed: {str(e)}")
            self.db.rollback()
            raise ValidationError(f"Profile update failed: {str(e)}")
    
    def create_user_response(self, profile: UserProfile, email: str) -> UserResponse:
        """Create user response from profile."""
        return UserResponse(
            id=profile.id,
            username=profile.username,
            email=email,
            phone=profile.phone,
            company=profile.company,
            profile_complete=profile.profile_complete,
            created_at=profile.created_at,
            updated_at=profile.updated_at
        )
    
    def delete_account(self, user_id: str) -> Dict[str, str]:
        """
        Delete user account and all related data.
        
        Args:
            user_id: User UUID
            
        Returns:
            Success message
            
        Raises:
            NotFoundError: If user not found
            ValidationError: If deletion fails
        """
        try:
            # First, check if user exists
            user = self.db.query(User).filter(User.id == user_id, User.is_active == True).first()
            
            if not user:
                raise NotFoundError("User profile")
            
            # Delete all user's reviews (cascade should handle this, but explicit is better)
            self.db.query(Review).filter(Review.user_id == user_id).delete()
            
            # Revoke all refresh tokens
            jwt_handler.revoke_all_user_tokens(user_id, self.db)
            
            # Mark user as inactive instead of hard delete (better for data integrity)
            user.is_active = False
            user.email = f"deleted_{user.id}@deleted.com"  # Prevent email conflicts
            user.username = f"deleted_{user.id}"  # Prevent username conflicts
            user.google_id = None  # Clear Google ID to allow re-signup with same Google account
            
            self.db.commit()
            
            logger.info(f"Account deletion completed for user {user_id}")
            return {"message": "Account deleted successfully"}
            
        except NotFoundError:
            raise
        except Exception as e:
            logger.error(f"Account deletion failed: {str(e)}")
            self.db.rollback()
            raise ValidationError(f"Account deletion failed: {str(e)}")
    
    def get_reviews_data(self) -> Dict[str, Any]:
        """Get sample reviews data (placeholder)."""
        from ..sample_reviews import get_reviews, calculate_dashboard_stats
        
        reviews = get_reviews()
        stats = calculate_dashboard_stats(reviews)
        
        return {
            "reviews": reviews,
            "stats": stats
        }
