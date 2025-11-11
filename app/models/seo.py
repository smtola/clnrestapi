from app.extensions import db
from datetime import datetime

class SEO(db.Model):
    __tablename__ = "seo"

    id = db.Column(db.Integer, primary_key=True)
    page = db.Column(db.String(255), unique=True, nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    keywords = db.Column(db.String(500), nullable=True)
    ogTitle = db.Column(db.String(255), nullable=True)
    ogDescription = db.Column(db.Text, nullable=True)
    ogImage = db.Column(db.String(500), nullable=True)
    url = db.Column(db.String(500), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
