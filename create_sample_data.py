import pandas as pd
import numpy as np
import os
from flask import Flask, render_template
from app import db, create_app
from app.models.models import Product, Brand

def create_sample_data():
    """
    Create sample data for development and testing
    """
    app = create_app()
    with app.app_context():
        # Check if there's already data in the database
        if Product.query.count() > 0:
            print("Database already contains data. Skipping sample data creation.")
            return
            
        # Create brands
        brands = [
            Brand(name="Nike"),
            Brand(name="Adidas"),
            Brand(name="Puma"),
            Brand(name="Reebok"),
            Brand(name="Under Armour"),
            Brand(name="New Balance")
        ]
        
        db.session.add_all(brands)
        db.session.commit()
        print(f"Added {len(brands)} sample brands")
        
        # Create products
        products = []
        genders = ["Men", "Women", "Unisex"]
        colors = ["Red", "Blue", "Green", "Black", "White", "Yellow", "Purple"]
        
        # Generate 20 sample products
        for i in range(1, 21):
            brand = np.random.choice(brands)
            price = round(np.random.uniform(500, 5000), 2)
            gender = np.random.choice(genders)
            color = np.random.choice(colors)
            
            product = Product(
                product_id=f"SAMPLE{i:03d}",
                name=f"Sample Product {i} by {brand.name}",
                brand_id=brand.id,
                gender=gender,
                price=price,
                num_images=np.random.randint(1, 6),
                description=f"This is a sample product description for product {i}. It is a {color} item designed for {gender}.",
                primary_color=color
            )
            products.append(product)
        
        db.session.add_all(products)
        db.session.commit()
        print(f"Added {len(products)} sample products")

if __name__ == "__main__":
    create_sample_data()
