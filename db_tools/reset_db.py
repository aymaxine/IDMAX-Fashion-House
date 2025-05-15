'''
This script will completely reset the database, create all tables, and set up admin user
'''

import os
import sys
from app import create_app, db
from app.models.models import User, Product, Brand

# Get the Flask app
app = create_app()

with app.app_context():
    print("Starting database reset...")
    
    # Drop all tables and recreate them
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    db.create_all()
    print("Tables created successfully!")
    
    # Create admin user
    print("Creating admin user...")
    admin = User(
        username="admin",
        email="admin@example.com",
        is_admin=True
    )
    admin.set_password("adminpass")
    db.session.add(admin)
    
    # Create regular user
    print("Creating regular user...")
    user = User(
        username="user",
        email="user@example.com",
        is_admin=False
    )
    user.set_password("userpass")
    db.session.add(user)
    
    # Create test brand
    print("Creating sample brand...")
    brand = Brand(
        name="Test Brand",
        description="This is a test brand for demonstration purposes."
    )
    db.session.add(brand)
    
    # Create test product
    print("Creating sample product...")
    product = Product(
        product_id="TEST001",
        name="Test Product",
        brand_id=1,  # Will link to the brand we just created
        description="This is a test product.",
        price=999.99,
        gender="Unisex",
        primary_color="Blue"
    )
    db.session.add(product)
    
    # Commit all changes
    db.session.commit()
    
    print("\nDatabase has been reset and populated with test data!")
    print("\nYou can log in with:")
    print("  Admin: username=admin, password=adminpass")
    print("  User: username=user, password=userpass")
    print("\nTest product and brand have been created.")
