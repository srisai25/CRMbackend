"""
Authentication routes.
"""
import logging
from fastapi import APIRouter, Depends
from fastapi.responses import RedirectResponse

from ..database import get_db
from ..config import config
from ..schemas import SignupRequest, LoginRequest, AuthResponse
from pydantic import BaseModel
from ..services import AuthService
from ..services.google_oauth_service import GoogleOAuthService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


class GoogleSignInRequest(BaseModel):
    """Google Sign-In request schema."""
    token: str  # Google ID token from frontend


@router.post("/signup", response_model=AuthResponse, status_code=201)
def signup(payload: SignupRequest, db=Depends(get_db)):
    """
    Register a new user.
    
    - **email**: User email address
    - **password**: Password (min 6 characters)
    - **username**: Username (3-50 characters)
    """
    auth_service = AuthService(db)
    return auth_service.signup(payload)


@router.post("/login", response_model=AuthResponse)
def login(payload: LoginRequest, db=Depends(get_db)):
    """
    Authenticate user.
    
    - **email**: User email address
    - **password**: User password
    """
    auth_service = AuthService(db)
    return auth_service.login(payload)


@router.post("/logout")
def logout(refresh_token: str, db=Depends(get_db)):
    """Logout current user by revoking refresh token."""
    auth_service = AuthService(db)
    return auth_service.logout(refresh_token)


@router.post("/refresh", response_model=AuthResponse)
def refresh_token(refresh_token: str, db=Depends(get_db)):
    """
    Refresh access token.
    
    - **refresh_token**: Valid refresh token
    """
    auth_service = AuthService(db)
    return auth_service.refresh_token(refresh_token)


@router.get("/google")
def google_oauth_start():
    """Start Google OAuth flow."""
    return RedirectResponse(url=f"{config.FRONTEND_URL}/auth/google")


@router.post("/google", response_model=AuthResponse)
def google_signin(payload: GoogleSignInRequest, db=Depends(get_db)):
    """
    Sign in with Google ID token.
    
    - **token**: Google ID token received from frontend
    """
    logger.info(f"🔵 Google sign-in request received with token length: {len(payload.token) if payload.token else 0}")
    
    try:
        google_service = GoogleOAuthService(db)
        result = google_service.google_signin(payload.token)
        logger.info(f"✅ Google sign-in successful for user: {result.get('user', {}).get('email', 'unknown')}")
        return result
    except Exception as e:
        logger.error(f"❌ Google sign-in failed: {str(e)}")
        raise
