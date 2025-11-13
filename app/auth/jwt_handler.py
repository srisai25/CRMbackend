"""
JWT authentication handler for MySQL-based authentication.
"""
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

from ..config import config
from ..models.db_models import User, RefreshToken
from ..exceptions import AuthenticationError

# Password hashing - using pbkdf2_sha256 to avoid bcrypt issues
pwd_context = CryptContext(
    schemes=["pbkdf2_sha256"], 
    deprecated="auto"
)


class JWTHandler:
    """Handles JWT token creation, validation, and user authentication."""
    
    def __init__(self):
        self.secret_key = config.JWT_SECRET_KEY
        self.algorithm = config.JWT_ALGORITHM
        self.access_token_expire_minutes = config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        self.refresh_token_expire_days = config.JWT_REFRESH_TOKEN_EXPIRE_DAYS
    
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"exp": expire, "type": "access"})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def create_refresh_token(self, user_id: str, db: Session) -> str:
        """Create and store refresh token."""
        # Generate unique token
        token = str(uuid.uuid4())
        expire = datetime.utcnow() + timedelta(days=self.refresh_token_expire_days)
        
        # Store in database
        refresh_token = RefreshToken(
            token=token,
            user_id=user_id,
            expires_at=expire
        )
        db.add(refresh_token)
        db.commit()
        
        return token
    
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode access token."""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            if payload.get("type") != "access":
                raise AuthenticationError("Invalid token type")
            
            return payload
        except JWTError:
            raise AuthenticationError("Invalid or expired token")
    
    def verify_refresh_token(self, token: str, db: Session) -> Optional[User]:
        """Verify refresh token and return associated user."""
        refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token == token,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
        
        if not refresh_token:
            raise AuthenticationError("Invalid or expired refresh token")
        
        return refresh_token.user
    
    def revoke_refresh_token(self, token: str, db: Session) -> bool:
        """Revoke a refresh token."""
        refresh_token = db.query(RefreshToken).filter(RefreshToken.token == token).first()
        if refresh_token:
            db.delete(refresh_token)
            db.commit()
            return True
        return False
    
    def revoke_all_user_tokens(self, user_id: str, db: Session) -> int:
        """Revoke all refresh tokens for a user."""
        count = db.query(RefreshToken).filter(RefreshToken.user_id == user_id).count()
        db.query(RefreshToken).filter(RefreshToken.user_id == user_id).delete()
        db.commit()
        return count
    
    def hash_password(self, password: str) -> str:
        """Hash a password."""
        return pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    def get_user_by_email(self, email: str, db: Session) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email, User.is_active == True).first()
    
    def get_user_by_id(self, user_id: str, db: Session) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id, User.is_active == True).first()
    
    def create_user(self, email: str, username: str, password: str, db: Session) -> User:
        """Create a new user."""
        # Check if user already exists
        if self.get_user_by_email(email, db):
            raise AuthenticationError("Email already registered")
        
        if db.query(User).filter(User.username == username).first():
            raise AuthenticationError("Username already taken")
        
        # Create user
        user = User(
            id=str(uuid.uuid4()),
            email=email,
            username=username,
            password_hash=self.hash_password(password),
            profile_complete=False
        )
        
        db.add(user)
        db.commit()
        db.refresh(user)
        
        return user
    
    def authenticate_user(self, email: str, password: str, db: Session) -> Optional[User]:
        """Authenticate user with email and password."""
        user = self.get_user_by_email(email, db)
        if not user:
            raise AuthenticationError("Account not found")
        if not self.verify_password(password, user.password_hash):
            raise AuthenticationError("Invalid password")
        return user


# Global JWT handler instance
jwt_handler = JWTHandler()
