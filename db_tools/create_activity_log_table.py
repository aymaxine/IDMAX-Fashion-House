"""
This script creates the activity_log table for tracking admin actions.
Run this script after making sure the models are properly imported.

Usage:
    python create_activity_log_table.py
"""
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.activity_log import ActivityLog

# Create a Flask application context
app = create_app()

with app.app_context():
    # Create the activity_log table
    try:
        ActivityLog.__table__.create(db.engine, checkfirst=True)
        print(f"✅ Activity log table created successfully.")
    except Exception as e:
        print(f"❌ Error creating activity log table: {str(e)}")
        
    print("\nNext steps:")
    print("1. Make sure you import ActivityLog in your models/__init__.py file")
    print("2. Import and use the log_activity function from app.utils.logging")
    print("3. Run your application and start tracking admin actions")
