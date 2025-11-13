"""
Authentication service - Business logic for auth operations.
"""
import logging
from typing import Dict
from sqlalchemy.orm import Session

from ..exceptions import AuthenticationError, DuplicateError
from ..models import UserProfile
from ..models.db_models import User
from ..schemas import SignupRequest, LoginRequest, AuthResponse, UserResponse
from ..auth import jwt_handler

logger = logging.getLogger(__name__)


class AuthService:
    """Handles authentication business logic."""
    
    def __init__(self, db: Session):
        self.db = db
    
    def signup(self, data: SignupRequest) -> AuthResponse:
        """
        Register a new user.
        
        Args:
            data: Signup request data
            
        Returns:
            AuthResponse with tokens and user
            
        Raises:
            DuplicateError: If username already exists
            AuthenticationError: If signup fails
        """
        try:
            # Create user using JWT handler
            user = jwt_handler.create_user(data.email, data.username, data.password, self.db)
            
            # Create tokens
            access_token = jwt_handler.create_access_token({"sub": user.id, "email": user.email})
            refresh_token = jwt_handler.create_refresh_token(user.id, self.db)
            
            # Create user response
            user_response = self._create_user_response(user)
            
            logger.info(f"User {data.username} registered successfully")
            
            return AuthResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                user=user_response
            )
            
        except AuthenticationError as e:
            if "Email already registered" in str(e):
                raise DuplicateError("Email")
            elif "Username already taken" in str(e):
                raise DuplicateError("Username")
            raise
        except Exception as e:
            logger.error(f"Signup failed: {str(e)}")
            raise AuthenticationError(f"Signup failed: {str(e)}")
    
    def login(self, data: LoginRequest) -> AuthResponse:
        """
        Authenticate user.
        
        Args:
            data: Login credentials
            
        Returns:
            AuthResponse with tokens and user
            
        Raises:
            AuthenticationError: If login fails
        """
        try:
            # Authenticate user
            user = jwt_handler.authenticate_user(data.email, data.password, self.db)
            
            # Create tokens
            access_token = jwt_handler.create_access_token({"sub": user.id, "email": user.email})
            refresh_token = jwt_handler.create_refresh_token(user.id, self.db)
            
            # Create user response
            user_response = self._create_user_response(user)
            
            logger.info(f"User {user.username} logged in")
            
            return AuthResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                user=user_response
            )
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            raise AuthenticationError("Login failed")
    
    def logout(self, refresh_token: str) -> Dict[str, str]:
        """Logout current user by revoking refresh token."""
        try:
            jwt_handler.revoke_refresh_token(refresh_token, self.db)
            return {"message": "Successfully logged out"}
        except Exception as e:
            logger.error(f"Logout failed: {str(e)}")
            raise AuthenticationError("Logout failed")
    
    def refresh_token(self, refresh_token: str) -> AuthResponse:
        """
        Refresh access token.
        
        Args:
            refresh_token: Valid refresh token
            
        Returns:
            AuthResponse with new tokens
            
        Raises:
            AuthenticationError: If refresh fails
        """
        try:
            # Verify refresh token and get user
            user = jwt_handler.verify_refresh_token(refresh_token, self.db)
            
            if not user:
                raise AuthenticationError("Invalid refresh token")
            
            # Create new tokens
            new_access_token = jwt_handler.create_access_token({"sub": user.id, "email": user.email})
            new_refresh_token = jwt_handler.create_refresh_token(user.id, self.db)
            
            # Revoke old refresh token
            jwt_handler.revoke_refresh_token(refresh_token, self.db)
            
            user_response = self._create_user_response(user)
            
            return AuthResponse(
                access_token=new_access_token,
                refresh_token=new_refresh_token,
                user=user_response
            )
            
        except AuthenticationError:
            raise
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise AuthenticationError("Token refresh failed")
    
    def _create_user_response(self, user: User) -> UserResponse:
        """Create user response from User model."""
        return UserResponse(
            id=user.id,
            username=user.username,
            email=user.email,
            phone=user.phone,
            company=user.company,
            google_maps_url=user.google_maps_url,
            profile_complete=user.profile_complete,
            created_at=user.created_at,
            updated_at=user.updated_at
        )
