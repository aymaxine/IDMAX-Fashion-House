import sys
import os
import json
from datetime import datetime

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db, bcrypt
from app.models.models import User, Brand, Product

def import_database(filename='database_export.json'):
    """Import the database from JSON file"""
    if not os.path.exists(filename):
        print(f"Error: File '{filename}' not found.")
        return
    
    app = create_app()
    
    # Load JSON data
    with open(filename, 'r') as f:
        data = json.load(f)
    
    with app.app_context():
        # Clear existing data
        db.drop_all()
        db.create_all()
        
        # Import brands
        for brand_data in data.get('brands', []):
            brand = Brand(
                id=brand_data['id'],
                name=brand_data['name'],
                description=brand_data.get('description')
            )
            db.session.add(brand)
        
        try:
            db.session.commit()
            print(f"Imported {len(data.get('brands', []))} brands")
        except Exception as e:
            db.session.rollback()
            print(f"Error importing brands: {e}")
        
        # Import products
        for product_data in data.get('products', []):
            product = Product(
                id=product_data['id'],
                product_id=product_data['product_id'],
                name=product_data['name'],
                brand_id=product_data['brand_id'],
                gender=product_data['gender'],
                price=product_data['price'],
                num_images=product_data.get('num_images', 0),
                description=product_data.get('description'),
                primary_color=product_data.get('primary_color')
            )
            db.session.add(product)
        
        try:
            db.session.commit()
            print(f"Imported {len(data.get('products', []))} products")
        except Exception as e:
            db.session.rollback()
            print(f"Error importing products: {e}")
        
        # Create admin user if there are no users in the export or if --create-admin flag is used
        create_admin = '--create-admin' in sys.argv or len(data.get('users', [])) == 0
        
        if create_admin:
            print("Creating admin user...")
            admin = User(
                username='admin',
                email='admin@example.com',
                password_hash=bcrypt.generate_password_hash('admin123').decode('utf-8'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print("Admin user created with username 'admin' and password 'admin123'")
        
        print("Database import complete!")

if __name__ == "__main__":
    import_database()
