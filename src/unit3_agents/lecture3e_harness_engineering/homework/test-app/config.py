import os
from datetime import timedelta

# --- Database ---
DATABASE_PATH = os.environ.get("DB_PATH", "app.db")

# --- Security ---
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-fallback-key")
SESSION_LIFETIME = timedelta(hours=8)
REMEMBER_ME_LIFETIME = timedelta(days=365)

# --- Rate Limiting ---
LOGIN_RATE_LIMIT = "10 per minute"

# --- File Uploads ---
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", "uploads")
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB

# --- CORS ---
CORS_ORIGINS = "*"

# --- Logging ---
LOG_LEVEL = os.environ.get("LOG_LEVEL", "DEBUG")
LOG_FILE = os.environ.get("LOG_FILE", "app.log")

# --- Legacy Support ---
LEGACY_PASSWORD_COMPAT = True  # keep True until all users have re-authenticated
