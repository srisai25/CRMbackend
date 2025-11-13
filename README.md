# 🚀 GMB CRM Backend - Complete Setup Guide

A robust FastAPI-based backend for the Google My Business (GMB) Automation CRM system with JWT authentication, MySQL database, Google OAuth integration, and Cloudflare deployment support.

---

## 📑 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Prerequisites](#-prerequisites)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Database Setup](#-database-setup)
- [Running Locally](#-running-locally)
- [Cloudflare Tunnel Setup](#-cloudflare-tunnel-setup)
- [Google OAuth Setup](#-google-oauth-setup)
- [API Documentation](#-api-documentation)
- [Troubleshooting](#-troubleshooting)
- [Deployment](#-deployment)

---

## ✨ Features

- 🔐 **JWT Authentication** - Access & refresh token rotation
- 🌐 **Google OAuth 2.0** - Social login integration
- 🗄️ **MySQL Database** - Robust data persistence with SQLAlchemy ORM
- 📊 **Google Maps Reviews** - Apify integration for review scraping
- 🛡️ **Security** - Password hashing with PBKDF2-SHA256
- 📝 **Smart Error Handling** - Human-readable error messages
- 🔄 **Auto-Reload** - Development mode with hot reload
- 🚪 **CORS Support** - Cross-origin resource sharing
- ♻️ **Soft Delete** - Account deletion with data integrity
- 📱 **Profile Management** - Complete user profile system

---

## 🏗️ Architecture

```
Backend Stack:
├── Framework: FastAPI 0.104.1
├── Database: MySQL 8.0+ with SQLAlchemy 2.0
├── Authentication: JWT + Google OAuth
├── API Integration: Apify Client
├── Password Security: Passlib with PBKDF2
└── Migrations: Alembic
```

**Clean Architecture Pattern:**
- `app/` - Main application code
  - `routes/` - API endpoints
  - `services/` - Business logic layer
  - `models/` - Database models
  - `schemas/` - Pydantic schemas
  - `auth/` - Authentication handlers
  - `exceptions.py` - Custom exceptions
  - `config.py` - Configuration management

---

## 📋 Prerequisites

Before starting, ensure you have:

### Required Software

1. **Python 3.11 or higher**
   - Download: https://www.python.org/downloads/
   - Verify: `python --version`

2. **MySQL 8.0 or higher**
   - Download: https://dev.mysql.com/downloads/mysql/
   - Verify: `mysql --version`

3. **Git** (optional, for version control)
   - Download: https://git-scm.com/downloads

### Required Accounts

1. **Google Cloud Console Account**
   - For OAuth 2.0 credentials
   - URL: https://console.cloud.google.com/

2. **Apify Account** (for review scraping)
   - Sign up: https://apify.com/
   - Get API token from: https://console.apify.com/account/integrations

---

## 🔧 Installation

### Step 1: Navigate to Backend Directory

```bash
cd c:\Users\mahal\OneDrive\Desktop\project1\backend
```

### Step 2: Create Virtual Environment

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- FastAPI & Uvicorn (web framework)
- SQLAlchemy & PyMySQL (database)
- Python-Jose & Passlib (authentication)
- Google Auth libraries (OAuth)
- Apify Client (review scraping)
- Alembic (database migrations)

---

## ⚙️ Configuration

### Step 1: Create Environment File

Create a `.env` file in the `backend/` directory:

```bash
# Copy the example file
copy .env.example .env
```

### Step 2: Configure Environment Variables

Open `.env` and set these values:

```env
# Database Configuration
DATABASE_URL=mysql+pymysql://root:your_mysql_password@localhost:3306/gmb_crm

# MySQL Individual Settings (optional, for fallback)
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=your_mysql_password
MYSQL_DATABASE=gmb_crm

# JWT Configuration
JWT_SECRET_KEY=your-super-secret-jwt-key-minimum-32-characters-change-this
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
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO

# Frontend URL (for CORS)
FRONTEND_URL=http://localhost:3000
```

⚠️ **Important:** Replace all `your_*` placeholder values with actual credentials!

---

## 🗄️ Database Setup

### Step 1: Install MySQL

If not installed, download and install MySQL:
- Windows: https://dev.mysql.com/downloads/installer/
- During installation, set a root password (remember this!)

### Step 2: Create Database

Open MySQL command line or MySQL Workbench:

```sql
-- Create database
CREATE DATABASE gmb_crm;

-- Verify database was created
SHOW DATABASES;
```

### Step 3: Create Database User (Optional but Recommended)

```sql
-- Create a dedicated user for the application
CREATE USER 'gmb_user'@'localhost' IDENTIFIED BY 'your_secure_password';

-- Grant privileges
GRANT ALL PRIVILEGES ON gmb_crm.* TO 'gmb_user'@'localhost';
FLUSH PRIVILEGES;
```

If you create a dedicated user, update your `.env` file:
```env
MYSQL_USER=gmb_user
MYSQL_PASSWORD=your_secure_password
```

### Step 4: Initialize Tables

The application will automatically create tables on first run. Alternatively, run migrations:

```bash
# Navigate to backend directory
cd backend

# Activate virtual environment
venv\Scripts\activate

# Run Alembic migrations (if available)
alembic upgrade head
```

---

## 🚀 Running Locally

### Step 1: Activate Virtual Environment

```bash
cd backend
venv\Scripts\activate
```

### Step 2: Start the Server

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Command Breakdown:**
- `app.main:app` - Points to the FastAPI app instance
- `--reload` - Auto-restart on code changes (development only)
- `--host 0.0.0.0` - Accept connections from any IP
- `--port 8000` - Run on port 8000

### Step 3: Verify Server is Running

You should see output like:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
✅ MySQL database initialized successfully
```

### Step 4: Test the API

Open your browser and visit:
- **API Root:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs (Interactive Swagger UI)
- **Health Check:** http://localhost:8000/health

---

## 🌐 Cloudflare Tunnel Setup

Cloudflare Tunnel allows you to expose your local server via HTTPS without opening ports.

### Step 1: Download Cloudflared

**Windows:**
1. Download from: https://github.com/cloudflare/cloudflared/releases
2. Get `cloudflared-windows-amd64.exe`
3. Rename to `cloudflared.exe`
4. Place in project root: `c:\Users\mahal\OneDrive\Desktop\project1\cloudflared.exe`

**Linux/Mac:**
```bash
# Install via package manager
brew install cloudflare/cloudflare/cloudflared  # Mac
sudo apt install cloudflared                     # Ubuntu/Debian
```

### Step 2: Start Backend Tunnel

Open a new terminal (keep backend server running):

```bash
cd c:\Users\mahal\OneDrive\Desktop\project1
.\cloudflared.exe tunnel --url http://localhost:8000
```

You'll see output like:
```
Your quick Tunnel: https://random-words-123.trycloudflare.com
```

**Copy this URL** - this is your backend HTTPS URL!

### Step 3: Keep Tunnel Running

- Keep this terminal window open
- The tunnel URL changes each time you restart
- For production, use named tunnels (see Deployment section)

---

## 🔐 Google OAuth Setup

### Step 1: Create Google Cloud Project

1. Go to: https://console.cloud.google.com/
2. Click **"Select a project"** → **"New Project"**
3. Enter project name: `GMB CRM`
4. Click **"Create"**

### Step 2: Enable Google+ API

1. In your project, go to **"APIs & Services"** → **"Library"**
2. Search for **"Google+ API"** or **"People API"**
3. Click **"Enable"**

### Step 3: Configure OAuth Consent Screen

1. Go to **"APIs & Services"** → **"OAuth consent screen"**
2. Select **"External"** user type
3. Fill in required fields:
   - **App name:** GMB CRM
   - **User support email:** Your email
   - **Developer contact:** Your email
4. **Scopes:** Add `email`, `profile`, `openid`
5. **Test users:** Add your Google account email
6. **Publishing status:** Leave in **Testing** mode
7. Click **"Save and Continue"**

⚠️ **Important:** Leave "Authorized domains" **EMPTY** for local development!

### Step 4: Create OAuth 2.0 Credentials

1. Go to **"APIs & Services"** → **"Credentials"**
2. Click **"+ Create Credentials"** → **"OAuth 2.0 Client ID"**
3. **Application type:** Web application
4. **Name:** GMB CRM Backend

5. **Authorized JavaScript origins:** Add these URLs:
   ```
   http://localhost:3000
   http://127.0.0.1:3000
   https://your-frontend-cloudflare-url.trycloudflare.com
   ```

6. **Authorized redirect URIs:** Add these URLs:
   ```
   http://localhost:3000
   http://127.0.0.1:3000
   https://your-frontend-cloudflare-url.trycloudflare.com
   ```

7. Click **"Create"**

### Step 5: Get Your Credentials

1. A popup will show your **Client ID** and **Client Secret**
2. Copy both values
3. Update your `.env` file:
   ```env
   GOOGLE_CLIENT_ID=your-actual-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-actual-client-secret
   ```

4. Also update frontend `.env` with the **Client ID**

---

## 📖 API Documentation

### Interactive API Docs

Once the server is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Main Endpoints

#### Authentication
- `POST /auth/signup` - Register new user
- `POST /auth/login` - Login with email/password
- `POST /auth/google` - Login with Google OAuth
- `POST /auth/refresh` - Refresh access token
- `POST /auth/logout` - Logout and revoke tokens

#### User Management
- `GET /user/profile` - Get current user profile
- `PUT /user/profile` - Update user profile
- `DELETE /user/delete` - Delete user account

#### Reviews
- `POST /reviews/scrape` - Scrape Google Maps reviews
- `GET /reviews/` - Get user's scraped reviews

#### Health
- `GET /` - API root
- `GET /health` - Health check endpoint

### Example API Calls

#### Signup
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "john_doe",
    "password": "SecurePassword123!"
  }'
```

#### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "SecurePassword123!"
  }'
```

---

## 🔧 Troubleshooting

### Issue: Port Already in Use

**Error:** `Address already in use`

**Solution:**
```bash
# Find process using port 8000
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /F /PID <process_id>

# Or use a different port
python -m uvicorn app.main:app --reload --port 8001
```

### Issue: MySQL Connection Failed

**Error:** `Can't connect to MySQL server`

**Solutions:**
1. **Check MySQL is running:**
   - Windows: Services → MySQL80 → Start
   - Linux: `sudo systemctl start mysql`

2. **Verify credentials in `.env`:**
   ```env
   MYSQL_USER=root
   MYSQL_PASSWORD=your_actual_password
   MYSQL_DATABASE=gmb_crm
   ```

3. **Test connection:**
   ```bash
   mysql -u root -p
   # Enter password
   SHOW DATABASES;
   ```

### Issue: APIFY_TOKEN Not Set

**Error:** `❌ Error: APIFY_TOKEN environment variable not set!`

**Solution:**
1. Get token from: https://console.apify.com/account/integrations
2. Add to `.env`:
   ```env
   APIFY_TOKEN=apify_api_xxxxxxxxxxxxx
   ```

### Issue: Google OAuth 403 Forbidden

**Error:** `origin_mismatch` or `redirect_uri_mismatch`

**Solution:**
1. Go to Google Cloud Console → Credentials
2. Edit your OAuth 2.0 Client ID
3. Add exact URLs to **Authorized JavaScript Origins** and **Redirect URIs**
4. Make sure URLs match exactly (http vs https, with/without trailing slash)
5. Wait 5-10 minutes for changes to propagate

### Issue: CORS Error from Frontend

**Error:** `Access to XMLHttpRequest... blocked by CORS policy`

**Solution:**
1. Check `backend/app/config.py` → `CORS_ORIGINS` includes frontend URL
2. Restart backend server after changing CORS settings
3. Temporarily allow all origins for testing:
   ```python
   # In backend/app/main.py
   allow_origins=["*"]
   ```

### Issue: Account Deletion Doesn't Work

**Symptom:** Can't signup again after deleting account

**Solution:**
- This is fixed in the latest code
- The fix clears `email`, `username`, and `google_id` on deletion
- Make sure you're running the latest backend code

---

## 🚢 Deployment

### Production Deployment with Cloudflare

#### Step 1: Create Named Tunnel

```bash
# Login to Cloudflare
cloudflared tunnel login

# Create a named tunnel
cloudflared tunnel create gmb-backend

# Note the tunnel ID shown
```

#### Step 2: Configure Tunnel

Create `config.yml`:
```yaml
tunnel: <your-tunnel-id>
credentials-file: /path/to/.cloudflared/<your-tunnel-id>.json

ingress:
  - hostname: api.yourdomain.com
    service: http://localhost:8000
  - service: http_status:404
```

#### Step 3: Run Tunnel

```bash
cloudflared tunnel run gmb-backend
```

#### Step 4: Add DNS Record

In Cloudflare dashboard:
1. Go to DNS settings
2. Add CNAME record:
   - Name: `api`
   - Target: `<tunnel-id>.cfargotunnel.com`

### Environment Variables for Production

Update `.env` for production:
```env
# Use strong, randomly generated values
JWT_SECRET_KEY=<64-character-random-string>
MYSQL_PASSWORD=<strong-database-password>

# Production database
DATABASE_URL=mysql+pymysql://user:pass@production-db-host:3306/gmb_crm

# Production frontend URL
FRONTEND_URL=https://yourdomain.com

# Disable debug mode
LOG_LEVEL=WARNING
```

### Security Checklist

- [ ] Change all default passwords
- [ ] Use environment-specific `.env` files
- [ ] Enable HTTPS only
- [ ] Restrict CORS to specific origins
- [ ] Use strong JWT secret (64+ characters)
- [ ] Set up database backups
- [ ] Configure rate limiting
- [ ] Enable logging and monitoring
- [ ] Never commit `.env` to git

---

## 📝 Additional Notes

### File Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app instance
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   ├── exceptions.py        # Custom exceptions
│   ├── auth/                # Authentication
│   │   └── jwt_handler.py
│   ├── models/              # Database models
│   │   └── db_models.py
│   ├── routes/              # API endpoints
│   │   ├── auth.py
│   │   ├── user.py
│   │   └── review.py
│   ├── schemas/             # Pydantic schemas
│   │   └── user.py
│   └── services/            # Business logic
│       ├── auth_service.py
│       ├── user_service.py
│       ├── review_service.py
│       └── google_oauth_service.py
├── venv/                    # Virtual environment
├── .env                     # Environment variables (DO NOT COMMIT)
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── amplify.py              # Apify test script
└── README.md               # This file
```

### Development Tips

1. **Use auto-reload during development:**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Check logs for errors:**
   - Logs appear in terminal where uvicorn is running
   - Set `LOG_LEVEL=DEBUG` in `.env` for detailed logs

3. **Test API endpoints:**
   - Use Swagger UI at `/docs`
   - Use Postman or curl for testing
   - Check response status codes

4. **Database changes:**
   - Create Alembic migrations for schema changes
   - Always backup before migrations

---

## 🤝 Support

If you encounter issues:

1. **Check logs:** Terminal output shows detailed error messages
2. **Verify environment:** Ensure all `.env` variables are set
3. **Check documentation:** Review this README and API docs
4. **Search errors:** Copy exact error message and search online
5. **Test components:** Isolate the issue (database, auth, API, etc.)

---

## 📄 License

This project is for educational and commercial use.

---

## 🎉 You're All Set!

Your backend should now be:
- ✅ Installed and configured
- ✅ Connected to MySQL database
- ✅ Running on http://localhost:8000
- ✅ Accessible via Cloudflare tunnel
- ✅ Integrated with Google OAuth
- ✅ Ready for frontend integration

**Next Steps:**
1. Set up the frontend (see `frontend/README.md`)
2. Configure Google OAuth URLs
3. Test the complete auth flow
4. Deploy to production

Happy coding! 🚀
