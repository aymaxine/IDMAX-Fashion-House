import pandas as pd
import os
from app import create_app, db
from app.models.models import Product, Brand

def load_data(csv_path):
    """
    Load data from CSV file into the database
    """
    # Create application context
    app = create_app()
    with app.app_context():
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        print("Loading data from CSV...")
        # Read CSV data
        df = pd.read_csv(csv_path)
        
        # Select only a subset if file is too large (> 7000 records)
        # Process all records regardless of size
        print(f"CSV contains {len(df)} records, loading all products...")
        
        # Extract unique brands and create them first
        print("Creating brands...")
        unique_brands = df['ProductBrand'].unique()
        brands_map = {}  # To store brand name -> id mapping
        
        for brand_name in unique_brands:
            brand = Brand(name=brand_name)
            db.session.add(brand)
            db.session.flush()  # Flush to get the brand ID
            brands_map[brand_name] = brand.id
        
        db.session.commit()
        print(f"Added {len(brands_map)} brands")
        
        # Add products
        print("Creating products...")
        batch_size = 500
        products = []
        
        for index, row in df.iterrows():
            product = Product(
                product_id=str(row['ProductID']),
                name=row['ProductName'],
                brand_id=brands_map[row['ProductBrand']],
                gender=row['Gender'],
                price=float(row['Price (INR)']),
                num_images=int(row['NumImages']),
                description=row['Description'],
                primary_color=row['PrimaryColor']
            )
            products.append(product)
            
            # Insert in batches to improve performance
            if len(products) >= batch_size:
                db.session.add_all(products)
                db.session.commit()
                products = []
                print(f"Processed {index+1}/{len(df)} products")
        
        # Add any remaining products
        if products:
            db.session.add_all(products)
            db.session.commit()
        
        print(f"Successfully loaded {len(df)} products from CSV")
        
        # Count records to verify
        product_count = Product.query.count()
        brand_count = Brand.query.count()
        print(f"Database contains {product_count} products and {brand_count} brands")

if __name__ == "__main__":
    # Get the path to the CSV file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(current_dir, 'products.csv')
    
    # Load data
    load_data(csv_path)
