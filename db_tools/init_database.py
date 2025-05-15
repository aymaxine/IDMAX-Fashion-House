import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.models import User, Brand, Product
import csv
import random
from datetime import datetime, timedelta
from faker import Faker

# Create the app with the factory
app = create_app()
fake = Faker()

def initialize_database():
    """Initialize the database with tables"""
    with app.app_context():
        # Create tables
        db.create_all()
        print("Database tables created successfully!")

def create_brands():
    """Create sample brands"""
    with app.app_context():
        if Brand.query.count() > 0:
            print("Brands already exist in the database.")
            return

        brands = [
            {'name': 'Nike', 'description': 'Global sports and athleisure brand known for innovative designs and high performance products.'},
            {'name': 'Adidas', 'description': 'German sportswear company offering a wide range of athletic and casual apparel.'},
            {'name': 'Puma', 'description': 'Sportswear brand focusing on running, training, and motorsports.'},
            {'name': 'Levi\'s', 'description': 'Iconic American brand known for denim jeans and casual wear.'},
            {'name': 'H&M', 'description': 'Swedish fast fashion retailer offering trendy clothing at affordable prices.'},
            {'name': 'Zara', 'description': 'Spanish fast fashion brand known for adapting runway designs quickly.'},
            {'name': 'Gap', 'description': 'American casual apparel brand focusing on classic, comfortable basics.'},
            {'name': 'Ralph Lauren', 'description': 'Luxury fashion brand known for classic American designs.'},
            {'name': 'Tommy Hilfiger', 'description': 'Premium lifestyle brand with preppy, classic American cool styles.'},
            {'name': 'Uniqlo', 'description': 'Japanese casual wear brand focusing on minimalist designs and quality basics.'}
        ]
        
        for brand_data in brands:
            brand = Brand(name=brand_data['name'], description=brand_data['description'])
            db.session.add(brand)
        
        db.session.commit()
        print(f"{len(brands)} sample brands created!")

def create_products(count=100):
    """Create sample products"""
    with app.app_context():
        if Product.query.count() > 0:
            print("Products already exist in the database.")
            return
            
        brands = Brand.query.all()
        if not brands:
            print("No brands found. Please create brands first.")
            return
            
        genders = ['Men', 'Women', 'Unisex']
        colors = ['Red', 'Blue', 'Green', 'Black', 'White', 'Yellow', 'Purple', 'Orange', 'Brown', 'Pink', 'Grey']
        color_hex = {
            'Red': '#ff0000', 
            'Blue': '#0000ff', 
            'Green': '#00ff00', 
            'Black': '#000000', 
            'White': '#ffffff',
            'Yellow': '#ffff00', 
            'Purple': '#800080', 
            'Orange': '#ffa500', 
            'Brown': '#a52a2a', 
            'Pink': '#ffc0cb',
            'Grey': '#808080'
        }
        
        product_types = ['T-shirt', 'Jeans', 'Dress', 'Sweater', 'Jacket', 'Shorts', 'Skirt', 'Hoodie', 'Shirt', 'Pants']
        
        # Create products
        for i in range(1, count + 1):
            brand = random.choice(brands)
            gender = random.choice(genders)
            color = random.choice(colors)
            product_type = random.choice(product_types)
            
            # Create product with random attributes
            product = Product(
                product_id=f"PROD{i:04d}",
                name=f"{brand.name} {color} {product_type} for {gender}",
                brand_id=brand.id,
                gender=gender,
                price=round(random.uniform(499, 9999), 2),  # Random price between 499 and 9999 INR
                description=fake.paragraph(nb_sentences=5),
                primary_color=color_hex[color],
                num_images=random.randint(1, 5),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 60))  # Random creation date
            )
            
            db.session.add(product)
            
        db.session.commit()
        print(f"{count} sample products created!")

if __name__ == "__main__":
    # Initialize database
    initialize_database()
    
    # Create sample data
    create_brands()
    create_products(count=100)
    
    print("Database initialization complete!")
