# GMB CRM Backend

A robust FastAPI-based backend for the Google My Business (GMB) Automation CRM system featuring JWT authentication, MySQL database, Google OAuth integration, and intelligent error handling.

## 🏗️ Architecture

- **Framework**: FastAPI 0.104.1 with async/await support
- **Database**: MySQL 8.0+ with SQLAlchemy 2.0 ORM
- **Authentication**: JWT with refresh token rotation + Google OAuth
- **Password Security**: PBKDF2-SHA256 with salt
- **Database Migrations**: Alembic for version control
- **API Integration**: Apify for Google Maps review scraping
- **Error Handling**: Human-readable error messages with proper HTTP status codes
- **Architecture Pattern**: Clean Architecture with service layer separation

## 📋 Requirements

- Python 3.11+
- MySQL 8.0+
- Virtual environment (recommended)

## 🚀 Setup

### 1. Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Database Setup

```sql
-- Create database
CREATE DATABASE gmb_crm;

-- Create user (optional)
CREATE USER 'gmb_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON gmb_crm.* TO 'gmb_user'@'localhost';
FLUSH PRIVILEGES;
```

### 4. Environment Configuration

Create `.env` file in the backend root directory:

```env
# Database Configuration
DATABASE_URL=mysql+pymysql://root:your_password@localhost:3306/gmb_crm

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-here-minimum-32-characters
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# Google OAuth Configuration
GOOGLE_CLIENT_ID=your-google-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-google-client-secret

# API Integration
APIFY_TOKEN=your_apify_token_here

# Application Configuration
APP_NAME=GMB CRM Backend
APP_VERSION=1.0.0
HOST=localhost
PORT=8000
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s

# CORS Configuration
CORS_ORIGINS=["http://localhost:3000", "http://localhost:3001", "http://127.0.0.1:3000"]

# Error Messages
ERROR_GENERIC=An unexpected error occurred. Please try again later.
```

### 5. Database Migrations

```bash
# Run migrations
alembic upgrade head
```

### 6. Start Server

```bash

python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 80000

```

## 📊 Database Schema

### Users Table
```sql
CREATE TABLE users (
    id CHAR(36) PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash TEXT,
    phone VARCHAR(20),
    company VARCHAR(100),
    google_maps_url TEXT,
    google_id VARCHAR(255) UNIQUE,
    profile_complete BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_google_id (google_id)
);
```

### Reviews Table
```sql
CREATE TABLE reviews (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    author VARCHAR(255),
    rating INT NOT NULL,
    text TEXT,
    date VARCHAR(50),
    source_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

### Refresh Tokens Table
```sql
CREATE TABLE refresh_tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id CHAR(36) NOT NULL,
    token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
```

## 🛠️ API Endpoints

### Authentication (`/auth`)
- `POST /auth/signup` - User registration with email/password
- `POST /auth/login` - User login with email/password
- `POST /auth/google` - Google OAuth authentication
- `POST /auth/logout` - User logout (revokes refresh token)
- `POST /auth/refresh` - Refresh access token

### User Management (`/user`)
- `GET /user/profile` - Get user profile
- `PUT /user/profile` - Update user profile
- `PUT /user/change-password` - Change password
- `DELETE /user/delete` - Delete account

### Reviews (`/reviews`)
- `POST /reviews/scrape` - Scrape Google Maps reviews
- `GET /reviews/` - Get user reviews

## 🔐 Authentication Flow

### Standard Email/Password Flow
1. **Registration/Login** → Returns access + refresh tokens + user profile
2. **API Requests** → Include `Authorization: Bearer <access_token>`
3. **Token Expiry** → Use refresh token to get new access token
4. **Logout** → Revoke refresh token

### Google OAuth Flow
1. **Frontend** → Initiates Google Sign-In
2. **Google** → Returns ID token to frontend
3. **Frontend** → Sends ID token to `/auth/google`
4. **Backend** → Validates token, creates/updates user, returns JWT tokens
5. **Subsequent requests** → Use JWT tokens as normal

### Error Handling
All authentication endpoints return human-readable error messages:
- `invalid_credentials` → "The email or password you entered is incorrect."
- `email_already_exists` → "An account with this email already exists."
- `token_expired` → "Your session has expired. Please log in again."

## 📁 Project Structure

```
backend/
├── app/
│   ├── auth/
│   │   ├── __init__.py
│   │   └── jwt_handler.py          # JWT token management
│   ├── models/
│   │   ├── __init__.py
│   │   ├── db_models.py           # SQLAlchemy models
│   │   ├── user.py                # User domain models
│   │   └── review.py              # Review domain models
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py                # Authentication routes
│   │   ├── user.py                # User management routes
│   │   └── reviews.py             # Review routes
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py                # Auth request/response schemas
│   │   └── user.py                # User schemas
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py        # Authentication business logic
│   │   ├── user_service.py        # User management logic
│   │   ├── google_oauth_service.py # Google OAuth integration
│   │   └── review_service.py      # Review scraping logic
│   ├── config.py                  # Configuration management
│   ├── database.py                # Database connection & initialization
│   ├── exceptions.py              # Custom exceptions with human-readable messages
│   ├── main.py                    # FastAPI application with error handlers
│   └── sample_reviews.py          # Sample data for development
├── migrations/                    # Alembic migrations
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## 🔧 Development

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Testing

```bash
# Run tests (if available)
pytest

# Run with coverage
pytest --cov=app
```

### Debugging

```bash
# Run with debug logging
uvicorn app.main:app --reload --log-level debug

# Access interactive API docs
# http://localhost:8000/docs
```

## 🚀 Deployment

### Environment Variables

```env
# Production database
DATABASE_URL=mysql+pymysql://user:password@host:port/database

# Strong JWT secret
JWT_SECRET_KEY=your-production-secret-key

# Apify token
APIFY_TOKEN=your_production_apify_token
```

### Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "app.main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000"]
```

### Production Checklist

- [ ] Set strong JWT_SECRET_KEY
- [ ] Configure production database
- [ ] Set up SSL/HTTPS
- [ ] Configure CORS for production frontend
- [ ] Set up monitoring and logging
- [ ] Configure backup strategy

## 🚨 Error Handling System

The backend implements a comprehensive error handling system with human-readable messages:

### Custom Exception Classes
```python
# Authentication errors
AuthenticationError("invalid_credentials")
→ "The email or password you entered is incorrect."

# Validation errors  
ValidationError("invalid_email")
→ "Please enter a valid email address."

# Google OAuth errors
GoogleOAuthError("invalid_google_token")
→ "Google authentication failed. Please try signing in again."
```

### Error Response Format
```json
{
  "detail": "Human-readable error message",
  "error": "Human-readable error message",
  "code": "error_code_for_frontend",
  "path": "/api/endpoint",
  "details": { "field": "specific_field" }
}
```

### HTTP Status Code Mapping
- `400` → Bad Request with specific validation errors
- `401` → Authentication required or failed
- `403` → Access denied
- `404` → Resource not found
- `409` → Duplicate resource (email/username exists)
- `422` → Validation failed
- `429` → Rate limit exceeded
- `500` → Internal server error

## 🔒 Security Features

- **Password Hashing**: PBKDF2-SHA256 with salt
- **JWT Security**: Secure token generation with expiration
- **Google OAuth**: Secure third-party authentication
- **Input Validation**: Pydantic models for all inputs
- **SQL Injection Protection**: SQLAlchemy ORM with parameterized queries
- **Authentication Required**: Protected endpoints with JWT verification
- **Token Rotation**: Refresh token mechanism with revocation
- **CORS Configuration**: Controlled cross-origin access
- **Error Information Leakage Prevention**: Generic error messages for production

## 📞 Troubleshooting

### Common Issues

1. **Database Connection Error**
   ```bash
   # Check MySQL service
   net start mysql  # Windows
   sudo systemctl start mysql  # Linux
   
   # Test connection
   mysql -u root -p
   ```

2. **Migration Issues**
   ```bash
   # Reset migrations (development only)
   alembic downgrade base
   alembic upgrade head
   ```

3. **Import Errors**
   ```bash
   # Ensure virtual environment is activated
   which python  # Should point to venv
   pip list  # Check installed packages
   ```

### Logs and Debugging

- Check server logs for detailed error information
- Use `/docs` endpoint for API testing
- Enable debug logging for development
- Monitor database queries with SQLAlchemy logging

---

**Status**: Production Ready
**Python Version**: 3.11+
**Database**: MySQL 8.0+
