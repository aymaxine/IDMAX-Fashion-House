"""
Check if users exist in the database
"""
from app import create_app, db
from app.models.models import User

# Create the Flask application
app = create_app()

with app.app_context():
    print("Users in database:")
    users = User.query.all()
    if users:
        for user in users:
            print(f"User: {user.username}, Email: {user.email}, Admin: {user.is_admin}")
    else:
        print("No users found in database.")
