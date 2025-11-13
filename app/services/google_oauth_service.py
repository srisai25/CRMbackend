"""
Google OAuth service for handling Google Sign-In integration.
"""
import logging
from typing import Optional, Dict, Any
from google.auth.transport import requests
from google.oauth2 import id_token
from sqlalchemy.orm import Session

from ..models.db_models import User
from ..auth.jwt_handler import JWTHandler
from ..exceptions import AuthenticationError, ValidationError
from ..config import config

logger = logging.getLogger(__name__)


class GoogleOAuthService:
    """Handles Google OAuth authentication and user creation."""
    
    def __init__(self, db: Session):
        self.db = db
        self.jwt_handler = JWTHandler()
    
    def verify_google_token(self, token: str) -> Dict[str, Any]:
        """
        Verify Google ID token and extract user information.
        
        Args:
            token: Google ID token from frontend
            
        Returns:
            Dict containing user information from Google
            
        Raises:
            AuthenticationError: If token is invalid
        """
        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                token, 
                requests.Request(), 
                config.GOOGLE_CLIENT_ID
            )
            
            # Verify the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise AuthenticationError("Invalid token issuer")
            
            return {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'name': idinfo.get('name', ''),
                'picture': idinfo.get('picture', ''),
                'email_verified': idinfo.get('email_verified', False)
            }
            
        except ValueError as e:
            logger.error(f"Google token verification failed: {str(e)}")
            raise AuthenticationError("Invalid Google token")
    
    def authenticate_or_create_user(self, google_user_info: Dict[str, Any]) -> User:
        """
        Authenticate existing user or create new user from Google info.
        
        Args:
            google_user_info: User information from Google
            
        Returns:
            User object
            
        Raises:
            ValidationError: If email is not verified
        """
        if not google_user_info.get('email_verified'):
            raise ValidationError("Google email not verified")
        
        email = google_user_info['email']
        
        # Check if user already exists
        existing_user = self.db.query(User).filter(
            User.email == email,
            User.is_active == True
        ).first()
        
        if existing_user:
            # Update user's Google info if needed
            if not existing_user.google_id:
                existing_user.google_id = google_user_info['google_id']
                self.db.commit()
            
            logger.info(f"Existing Google user authenticated: {email}")
            return existing_user
        
        # Create new user from Google info
        username = self._generate_username_from_email(email)
        
        import uuid
        new_user = User(
            id=str(uuid.uuid4()),  # Generate UUID for new user
            email=email,
            username=username,
            google_id=google_user_info['google_id'],
            password_hash=None,  # No password for Google users
            profile_complete=False,  # They'll need to complete profile
            is_active=True
        )
        
        self.db.add(new_user)
        self.db.commit()
        self.db.refresh(new_user)
        
        logger.info(f"New Google user created: {email}")
        return new_user
    
    def _generate_username_from_email(self, email: str) -> str:
        """
        Generate a unique username from email.
        
        Args:
            email: User's email address
            
        Returns:
            Unique username
        """
        base_username = email.split('@')[0]
        username = base_username
        counter = 1
        
        # Ensure username is unique
        while self.db.query(User).filter(User.username == username).first():
            username = f"{base_username}{counter}"
            counter += 1
        
        return username
    
    def google_signin(self, token: str) -> Dict[str, Any]:
        """
        Complete Google Sign-In flow.
        
        Args:
            token: Google ID token
            
        Returns:
            Dict containing JWT tokens and user info
        """
        # Verify Google token and get user info
        google_user_info = self.verify_google_token(token)
        
        # Authenticate or create user
        user = self.authenticate_or_create_user(google_user_info)
        
        # Generate JWT tokens
        access_token = self.jwt_handler.create_access_token({"sub": user.id})
        refresh_token = self.jwt_handler.create_refresh_token(user.id, self.db)
        
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "phone": user.phone,
                "company": user.company,
                "profile_complete": user.profile_complete,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            }
        }
