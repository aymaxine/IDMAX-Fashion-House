"""
Create all necessary tables and relationships for the application
"""
import os
from app import create_app, db
from app.models.models import Product, Brand, User
from app.models.activity_log import ActivityLog
from app.models.product_image import ProductImage

# Create Flask app with development configuration
app = create_app()

# Create application context
with app.app_context():
    print("Creating database tables...")
    db.create_all()
    print("Database tables created successfully!")
