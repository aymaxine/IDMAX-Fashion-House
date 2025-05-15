import sys
import os
import sqlite3
import json
from datetime import datetime

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.models import User, Brand, Product

def export_database():
    """Export the database to JSON for easy import during deployment"""
    app = create_app()
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "brands": [],
        "products": [],
        "users": []
    }
    
    with app.app_context():
        # Export brands
        brands = Brand.query.all()
        for brand in brands:
            brand_data = {
                "id": brand.id,
                "name": brand.name,
                "description": brand.description,
                "created_at": brand.created_at.isoformat() if brand.created_at else None,
                "updated_at": brand.updated_at.isoformat() if brand.updated_at else None
            }
            data["brands"].append(brand_data)
        
        # Export products
        products = Product.query.all()
        for product in products:
            product_data = {
                "id": product.id,
                "product_id": product.product_id,
                "name": product.name,
                "brand_id": product.brand_id,
                "gender": product.gender,
                "price": product.price,
                "num_images": product.num_images,
                "description": product.description,
                "primary_color": product.primary_color,
                "created_at": product.created_at.isoformat() if product.created_at else None,
                "updated_at": product.updated_at.isoformat() if product.updated_at else None
            }
            data["products"].append(product_data)
        
        # Export users (excluding password_hash for security)
        users = User.query.all()
        for user in users:
            user_data = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat() if user.created_at else None
            }
            data["users"].append(user_data)
    
    # Write to JSON file
    with open('database_export.json', 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"Database export complete: {len(data['brands'])} brands, {len(data['products'])} products, {len(data['users'])} users")

if __name__ == "__main__":
    export_database()
