import os
import secrets
from datetime import timedelta
import warnings

# Generate a random  (256-bit) hex string
SECRET_KEY = secrets.token_hex(64)

# Use a fixed default JWT secret key for development consistency
# In production, always set JWT_SECRET_KEY as an environment variable
# This fixed key ensures tokens remain valid across server restarts in development
DEFAULT_JWT_SECRET_KEY = "dev-jwt-secret-key-change-in-production-please-set-jwt-secret-key-env-var"

class Config:
    SCHEDULER_API_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)
    
    # JWT_SECRET_KEY: Use environment variable if set, otherwise use fixed default
    # This ensures tokens remain valid across restarts in development
    # WARNING: In production, always set JWT_SECRET_KEY as an environment variable
    _jwt_secret = os.environ.get('JWT_SECRET_KEY')
    if not _jwt_secret:
        warnings.warn(
            "JWT_SECRET_KEY not set in environment. Using default key. "
            "This is insecure for production! Set JWT_SECRET_KEY environment variable.",
            UserWarning
        )
        _jwt_secret = DEFAULT_JWT_SECRET_KEY
    
    # Ensure JWT_SECRET_KEY is properly set as a string
    JWT_SECRET_KEY = str(_jwt_secret) if _jwt_secret else DEFAULT_JWT_SECRET_KEY
    
    # JWT Algorithm - explicitly set to HS256 (default, but good to be explicit)
    JWT_ALGORITHM = 'HS256'
    
    # JWT Token expiration settings - tokens are reusable until they expire
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # Access token valid for 24 hours
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # Refresh token valid for 30 days
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://Tola2025:Tola2025@cluster0.l14xytm.mongodb.net/cln_db?retryWrites=true&w=majority&appName=Cluster0')
    SWAGGER = {
        'title': 'CLN REST API',
        'uiversion': 3
    }