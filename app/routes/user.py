"""
User routes.
"""
import logging
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from ..database import get_db
from ..models import UserProfile, UserUpdate
from ..models.db_models import User
from ..schemas import UserResponse, UserUpdateRequest
from pydantic import BaseModel, Field
from ..services import UserService
from ..exceptions import AuthenticationError
from ..auth import jwt_handler

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/user", tags=["User"])
security = HTTPBearer()


class PasswordChangeRequest(BaseModel):
    """Password change request schema."""
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db=Depends(get_db)
) -> UserProfile:
    """
    Get current authenticated user.
    
    Args:
        credentials: Bearer token
        db: Database session
        
    Returns:
        UserProfile
        
    Raises:
        AuthenticationError: If token invalid
    """
    token = credentials.credentials
    
    try:
        logger.info(f"🔐 Authenticating user with token: {token[:20]}...")
        
        # Verify JWT token
        payload = jwt_handler.verify_access_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            logger.error("❌ Invalid token - no user ID found")
            raise AuthenticationError("Invalid token format")
        
        logger.info(f"📋 Token verified for user: {user_id}")
        
        # Get profile
        user_service = UserService(db)
        profile = user_service.get_profile(user_id)
        
        logger.info(f"✅ User authenticated successfully: {user_id}")
        return profile
        
    except AuthenticationError as e:
        logger.error(f"❌ Authentication error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        logger.error(f"💥 Auth failed with exception: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Authentication failed: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.get("/profile", response_model=UserResponse)
def get_profile(
    current_user: UserProfile = Depends(get_current_user),
    db=Depends(get_db)
):
    """Get current user profile."""
    # Get user from database to get email
    user = db.query(User).filter(User.id == current_user.id).first()
    email = user.email if user else None
    
    user_service = UserService(db)
    return user_service.create_user_response(current_user, email)


@router.put("/profile", response_model=UserResponse)
def update_profile(
    payload: UserUpdateRequest,
    current_user: UserProfile = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Update current user profile.
    
    - **username**: New username (optional)
    - **phone**: Phone number (optional)
    - **company**: Company name (optional)
    - **google_maps_url**: Google Maps business URL (optional)
    """
    user_service = UserService(db)
    
    # Convert to domain model
    update_data = UserUpdate(**payload.dict(exclude_unset=True))
    
    # Update profile
    updated_user = user_service.update_profile(current_user.id, update_data)
    
    # Get email from database
    user = db.query(User).filter(User.id == current_user.id).first()
    email = user.email if user else None
    
    return user_service.create_user_response(updated_user, email)


@router.put("/change-password")
def change_password(
    payload: PasswordChangeRequest,
    current_user: UserProfile = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Change user password.
    
    - **current_password**: Current password for verification
    - **new_password**: New password (minimum 6 characters)
    """
    try:
        # Get user from database
        user = db.query(User).filter(User.id == current_user.id, User.is_active == True).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Verify current password
        if not jwt_handler.verify_password(payload.current_password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )
        
        # Update password
        user.password_hash = jwt_handler.hash_password(payload.new_password)
        db.commit()
        
        logger.info(f"Password changed successfully for user {current_user.id}")
        
        return {"message": "Password changed successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Password change failed for user {current_user.id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Password change failed. Please try again."
        )


@router.delete("/delete")
def delete_account(
    current_user: UserProfile = Depends(get_current_user),
    db=Depends(get_db)
):
    """
    Delete current user account and all related data.
    
    This action is irreversible and will:
    - Delete the user profile
    - Delete all related user data
    - Remove the user from authentication system
    
    Returns:
        Success message confirming account deletion
    """
    logger.info(f"🗑️ Delete account request received for user: {current_user.id}")
    
    user_service = UserService(db)
    
    try:
        logger.info(f"📋 User details: username={current_user.username}, email=<redacted>")
        
        result = user_service.delete_account(current_user.id)
        
        logger.info(f"✅ Account deletion completed successfully for user {current_user.id}")
        return result
        
    except Exception as e:
        logger.error(f"💥 Account deletion failed for user {current_user.id}: {str(e)}", exc_info=True)
        
        # Return more specific error information
        error_detail = f"Account deletion failed: {str(e)}"
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_detail
        )


@router.get("/dashboard/stats")
def get_dashboard_stats(current_user: UserProfile = Depends(get_current_user)):
    """Get dashboard statistics (protected)."""
    user_service = UserService(None)
    return user_service.get_reviews_data()


@router.get("/reviews")
def get_reviews(current_user: UserProfile = Depends(get_current_user)):
    """Get all reviews (protected)."""
    user_service = UserService(None)
    return user_service.get_reviews_data()


# Public endpoints
@router.get("/public/dashboard/stats", include_in_schema=False)
def get_public_dashboard_stats():
    """Get dashboard statistics (public)."""
    from ..sample_reviews import get_reviews, calculate_dashboard_stats
    reviews = get_reviews()
    stats = calculate_dashboard_stats(reviews)
    return {"reviews": reviews, "stats": stats}


@router.get("/public/reviews", include_in_schema=False)
def get_public_reviews():
    """Get all reviews (public)."""
    from ..sample_reviews import get_reviews
    reviews = get_reviews()
    return {"reviews": reviews, "total": len(reviews)}
