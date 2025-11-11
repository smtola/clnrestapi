import os
import secrets
# Generate a random 32-byte (256-bit) hex string
SECRET_KEY = secrets.token_hex(32)
JWT_SECRET_KEY = secrets.token_hex(64)

class Config:
    SCHEDULER_API_ENABLED = True
    SECRET_KEY = os.environ.get('SECRET_KEY', SECRET_KEY)
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', JWT_SECRET_KEY)
    MONGO_URI = os.environ.get('MONGO_URI', 'mongodb+srv://Tola2025:Tola2025@cluster0.l14xytm.mongodb.net/cln_db?retryWrites=true&w=majority&appName=Cluster0')
    SWAGGER = {
        'title': 'CLN REST API',
        'uiversion': 3
    }