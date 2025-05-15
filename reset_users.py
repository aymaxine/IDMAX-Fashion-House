"""
Reset and create a fresh admin user
"""
from app import create_app, db, bcrypt
from app.models.models import User
import os

# Create the Flask application
app = create_app()

def reset_and_create_admin():
    """Reset the users table and create a fresh admin user"""
    with app.app_context():
        print("Resetting users table and creating a fresh admin user...")
        
        # Drop users table and recreate it
        try:
            # Delete all users first
            User.query.delete()
            db.session.commit()
            print("All existing users deleted")
        except Exception as e:
            db.session.rollback()
            print(f"Error clearing users: {e}")
            
        # Create admin user with properly hashed password
        admin_username = "admin"
        admin_email = "admin@example.com"
        admin_password = "adminpass"  # You should use a strong password in production
        
        # Use Flask-Bcrypt directly
        hashed_password = bcrypt.generate_password_hash(admin_password).decode('utf-8')
        
        # Create new admin user
        admin = User(
            username=admin_username,
            email=admin_email,
            password_hash=hashed_password,
            is_admin=True
        )
        
        # Add and commit to database
        try:
            db.session.add(admin)
            db.session.commit()
            print(f"Admin user created successfully!")
            print(f"  Username: {admin_username}")
            print(f"  Password: {admin_password}")
            print(f"  Email: {admin_email}")
            print("\nYou can now log in with these credentials.")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin: {e}")
            
        # Create regular test user
        user_username = "user"
        user_email = "user@example.com" 
        user_password = "userpass"
        
        # Hash the user password
        hashed_password = bcrypt.generate_password_hash(user_password).decode('utf-8')
        
        # Create regular user
        regular_user = User(
            username=user_username,
            email=user_email,
            password_hash=hashed_password,
            is_admin=False
        )
        
        # Add and commit to database
        try:
            db.session.add(regular_user)
            db.session.commit()
            print(f"\nRegular user created successfully!")
            print(f"  Username: {user_username}")
            print(f"  Password: {user_password}")
            print(f"  Email: {user_email}")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating regular user: {e}")

if __name__ == "__main__":
    reset_and_create_admin()
