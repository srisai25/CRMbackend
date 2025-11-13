"""
Custom exceptions for better error handling with human-readable messages.
"""
from fastapi import HTTPException, status
from typing import Dict, Any


class AppError(HTTPException):
    """Base application error with enhanced error details."""
    def __init__(
        self, 
        message: str, 
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        error_code: str = None,
        details: Dict[str, Any] = None
    ):
        self.error_code = error_code
        self.details = details or {}
        super().__init__(status_code=status_code, detail=message)


class AuthenticationError(AppError):
    """Authentication failed with specific error codes."""
    def __init__(self, message: str = None, error_code: str = "authentication_failed"):
        messages = {
            "invalid_credentials": "The email or password you entered is incorrect.",
            "token_expired": "Your session has expired. Please log in again.",
            "invalid_token": "Invalid authentication token. Please log in again.",
            "authentication_failed": "Authentication failed. Please check your credentials."
        }
        final_message = message or messages.get(error_code, messages["authentication_failed"])
        super().__init__(final_message, status.HTTP_401_UNAUTHORIZED, error_code)


class NotFoundError(AppError):
    """Resource not found with specific error codes."""
    def __init__(self, resource: str = "Resource", error_code: str = "not_found"):
        messages = {
            "user_not_found": "User account not found.",
            "profile_not_found": "User profile not found.",
            "business_not_found": "Business not found at the provided URL.",
            "reviews_not_found": "No reviews found for this business.",
            "not_found": f"{resource} not found."
        }
        message = messages.get(error_code, f"{resource} not found")
        super().__init__(message, status.HTTP_404_NOT_FOUND, error_code)


class DuplicateError(AppError):
    """Resource already exists with specific error codes."""
    def __init__(self, resource: str = "Resource", error_code: str = "duplicate"):
        messages = {
            "email_already_exists": "An account with this email already exists. Try logging in instead.",
            "username_already_exists": "This username is already taken. Please choose a different one.",
            "duplicate": f"{resource} already exists."
        }
        message = messages.get(error_code, f"{resource} already exists")
        super().__init__(message, status.HTTP_409_CONFLICT, error_code)


class ValidationError(AppError):
    """Validation failed with specific error codes."""
    def __init__(self, message: str = None, error_code: str = "validation_failed", field: str = None):
        messages = {
            "invalid_email": "Please enter a valid email address.",
            "weak_password": "Password must be at least 8 characters long and contain letters and numbers.",
            "invalid_phone": "Please enter a valid phone number.",
            "invalid_maps_url": "Please provide a valid Google Maps business URL.",
            "validation_failed": "Please check your input - some fields contain invalid data."
        }
        final_message = message or messages.get(error_code, messages["validation_failed"])
        details = {"field": field} if field else {}
        super().__init__(final_message, status.HTTP_422_UNPROCESSABLE_ENTITY, error_code, details)


class DatabaseError(AppError):
    """Database operation failed."""
    def __init__(self, message: str = None, error_code: str = "database_error"):
        messages = {
            "connection_failed": "Database connection failed. Please try again later.",
            "query_failed": "Database query failed. Please try again.",
            "database_error": "A database error occurred. Please try again later."
        }
        final_message = message or messages.get(error_code, messages["database_error"])
        super().__init__(final_message, status.HTTP_500_INTERNAL_SERVER_ERROR, error_code)


class GoogleOAuthError(AppError):
    """Google OAuth specific errors."""
    def __init__(self, message: str = None, error_code: str = "google_auth_failed"):
        messages = {
            "invalid_google_token": "Google authentication failed. Please try signing in again.",
            "google_account_disabled": "Your Google account access has been restricted.",
            "google_auth_failed": "Google Sign-In failed. Please try again."
        }
        final_message = message or messages.get(error_code, messages["google_auth_failed"])
        super().__init__(final_message, status.HTTP_401_UNAUTHORIZED, error_code)


class RateLimitError(AppError):
    """Rate limiting errors."""
    def __init__(self, message: str = "Too many requests. Please wait before trying again."):
        super().__init__(message, status.HTTP_429_TOO_MANY_REQUESTS, "rate_limit_exceeded")


class BusinessLogicError(AppError):
    """Business logic validation errors."""
    def __init__(self, message: str, error_code: str = "business_logic_error"):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, error_code)
