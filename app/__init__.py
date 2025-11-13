from flask import Flask, send_from_directory
from flask_cors import CORS
from .config import Config
from .extensions import mongo, jwt, swagger
from .routes.auth import auth_bp
from .routes.web import web_bp
from .routes.seo import seo_bp
import os
from flask_apscheduler import APScheduler
from datetime import datetime, timedelta, timezone
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(
        __name__,
        static_folder=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'static'),
        static_url_path='/static'
    )

    app.config.from_object(Config)

    # Verify JWT_SECRET_KEY is set
    if not app.config.get('JWT_SECRET_KEY'):
        raise ValueError("JWT_SECRET_KEY must be set in configuration")

    # ----------------- Extensions -----------------
    mongo.init_app(app)
    jwt.init_app(app)
    swagger.init_app(app)

    # ----------------- CORS -----------------
    # Allow React frontend with Authorization header
    CORS(
        app,
        resources={r"/api/*": {"origins": "*"}},
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"]
    )

    # ----------------- Blueprints -----------------
    app.register_blueprint(auth_bp, url_prefix="/api/v1/docs/auth")
    app.register_blueprint(web_bp, url_prefix="/api/v1/docs/web")
    app.register_blueprint(seo_bp, url_prefix="/api/v1/docs/seo")
    # ----------------- Serve Static Files -----------------
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        return send_from_directory(app.static_folder, filename)

    # ----------------- Scheduler -----------------
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.add_job(
        id="delete_unverified",
        func=delete_unverified_accounts,
        trigger="interval",
        minutes=30
    )
    scheduler.start()
    
    return app

def delete_unverified_accounts():
    """
    Delete unverified accounts older than 1 minutes
    """
    cutoff = datetime.utcnow() - timedelta(minutes=1)
    result = mongo.db.users.delete_many({
        "is_verified": False,
        "created_at": {"$lte": cutoff}
    })
    print(f"Deleted {result.deleted_count} unverified accounts")