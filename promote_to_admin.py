#!/usr/bin/env python
"""
Script to promote an existing user to admin status.
Run with: python promote_to_admin.py

This script allows promoting a regular user to admin status by entering their username or email.
"""
import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.models import User

# Create the app with the factory
app = create_app()

def promote_to_admin():
    """Promote an existing user to admin"""
    with app.app_context():
        # Get user identifier
        identifier = input("Enter the username or email of the user to promote: ")
        
        # Find the user
        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier)
        ).first()
        
        if not user:
            print(f"No user found with username or email: {identifier}")
            return
            
        if user.is_admin:
            print(f"User {user.username} is already an admin.")
            return
            
        # Confirm promotion
        confirm = input(f"Promote {user.username} ({user.email}) to admin? (y/n): ")
        if confirm.lower() != 'y':
            print("Operation cancelled.")
            return
            
        # Promote user
        user.is_admin = True
        db.session.commit()
        print(f"✅ User {user.username} has been promoted to admin!")

if __name__ == "__main__":
    promote_to_admin()
