import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db, bcrypt
from app.models.models import User
from getpass import getpass

# Create the app with the factory
app = create_app()

def create_admin():
    """Create an admin user"""
    with app.app_context():
        # Check if any admin exists
        admin_exists = User.query.filter_by(is_admin=True).first()
        if admin_exists:
            print(f"An admin user already exists: {admin_exists.username}")
            create_another = input("Do you want to create another admin? (y/n): ")
            if create_another.lower() != 'y':
                return
        
        username = input("Enter admin username: ")
        email = input("Enter admin email: ")
        
        # Check if username or email already exists
        user_exists = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()
        
        if user_exists:
            print("Username or email already exists!")
            return
        
        # Get password securely
        while True:
            password = getpass("Enter password: ")
            confirm_password = getpass("Confirm password: ")
            
            if password != confirm_password:
                print("Passwords don't match, try again.")
            else:
                break
        
        # Create the admin user
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        admin = User(username=username, email=email, password_hash=hashed_password, is_admin=True)
        
        db.session.add(admin)
        db.session.commit()
        
        print(f"Admin user '{username}' created successfully!")


if __name__ == "__main__":
    create_admin()
