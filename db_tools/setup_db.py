"""
Initialize the database for the Fashion Catalog application
"""
from app import create_app, db
from app.models.models import User

# Create the Flask application
app = create_app()

# Push an application context
with app.app_context():
    # Create all database tables
    db.create_all()
    print("Database tables created successfully!")
    
    # Create an admin user if none exists
    admin = User.query.filter_by(is_admin=True).first()
    if not admin:
        admin = User(
            username="admin",
            email="admin@example.com",
            is_admin=True
        )
        admin.set_password("adminpass")
        db.session.add(admin)
        db.session.commit()
        print("Admin user created!")
        print("Username: admin")
        print("Password: adminpass")
    else:
        print("Admin user already exists.")
        
    # Create a regular user for testing
    user = User.query.filter_by(username="user").first()
    if not user:
        user = User(
            username="user",
            email="user@example.com",
            is_admin=False
        )
        user.set_password("userpass")
        db.session.add(user)
        db.session.commit()
        print("Regular user created!")
        print("Username: user")
        print("Password: userpass")
    else:
        print("Regular user already exists.")
        
print("Database initialization completed!")
