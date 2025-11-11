import os
import secrets
from datetime import timedelta
# Generate a random 32-byte (256-bit) hex string
SECRET_KEY = secrets.token_hex(32)
JWT_SECRET_KEY = secrets.token_hex(64)

class Config:
    SCHEDULER_API_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', JWT_SECRET_KEY)
    # JWT Token expiration settings - tokens are reusable until they expire
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24)  # Access token valid for 24 hours
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)  # Refresh token valid for 30 days
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://Tola2025:Tola2025@cluster0.l14xytm.mongodb.net/cln_db?retryWrites=true&w=majority&appName=Cluster0')
    SWAGGER = {
        'title': 'CLN REST API',
        'uiversion': 3
    }