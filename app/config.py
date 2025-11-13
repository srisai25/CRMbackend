"""
Centralized configuration for the application.
All hardcoded values should be moved here.
"""
import os
from typing import List
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration class."""
    
    # Application
    APP_NAME = "GMB Automation CRM API"
    APP_VERSION = "1.0.0"
    
    # Server
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    
    # Frontend
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:3000")
    
    # CORS
    CORS_ORIGINS = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://localhost:3002",
    ]
    
    # Database - MySQL
    MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
    MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
    MYSQL_USER = os.getenv("MYSQL_USER", "root")
    MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
    MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "gmb_crm")
    
    # Database URL for SQLAlchemy
    # Handle the case where DATABASE_URL has placeholder password
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        # Fallback to SQLite for development if MySQL not configured
        try:
            # Try MySQL first
            database_url = f"mysql+pymysql://{MYSQL_USER}:{MYSQL_PASSWORD}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DATABASE}"
        except:
            # Fallback to SQLite
            database_url = "sqlite:///./gmb_crm.db"
    
    if "your_mysql_password" in database_url:
        database_url = database_url.replace("your_mysql_password", MYSQL_PASSWORD)
    DATABASE_URL = database_url
    
    # Apify Configuration
    APIFY_TOKEN: str = os.getenv("APIFY_TOKEN", "")
    
    # Google OAuth Configuration
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    
    # Frontend URL for redirects
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "http://localhost:3001")
    
    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    # Logging
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # HTTP Status Messages
    ERROR_GENERIC = "An error occurred while processing your request"
    ERROR_AUTH_INVALID = "Invalid authentication credentials"
    ERROR_NOT_FOUND = "Resource not found"
    ERROR_DUPLICATE = "Resource already exists"
    
    SUCCESS_LOGIN = "Login successful"
    SUCCESS_LOGOUT = "Logout successful"
    SUCCESS_SIGNUP = "Account created successfully"


# Global config instance
config = Config()
