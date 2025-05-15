"""
Reset num_images field for products that don't have actual image records.

This script identifies products that have num_images > 0 but don't have 
corresponding records in the product_images table, and resets their num_images to 0.
"""

from app import create_app, db
from app.models.models import Product
from app.models.product_image import ProductImage
from sqlalchemy import func

def reset_image_counts():
    """Reset num_images for products without actual images"""
    app = create_app()
    with app.app_context():
        # First, print some stats
        total_products = Product.query.count()
        products_with_images_count = Product.query.filter(Product.num_images > 0).count()
        actual_images_count = ProductImage.query.count()
        
        print(f"Database contains {total_products} products")
        print(f"{products_with_images_count} products have num_images > 0")
        print(f"Actual image records in database: {actual_images_count}")
        
        # Get count of actual images per product
        product_image_counts = db.session.query(
            ProductImage.product_id,
            func.count(ProductImage.id).label('actual_count')
        ).group_by(ProductImage.product_id).all()
        
        print(f"Found {len(product_image_counts)} products with actual images")
        
        # Create a dictionary of product_id -> actual_image_count
        image_count_dict = {pid: count for pid, count in product_image_counts}
        
        # Get products with num_images > 0
        products_with_images = Product.query.filter(Product.num_images > 0).all()
        print(f"Processing {len(products_with_images)} products with num_images > 0")
        
        # Counter for products that need updating
        updated_count = 0
        
        # For each product, check if it has actual images
        for product in products_with_images:
            actual_count = image_count_dict.get(product.id, 0)
            
            # If num_images doesn't match actual image count, update it
            if product.num_images != actual_count:
                product.num_images = actual_count
                updated_count += 1
                
        # Commit the changes
        if updated_count > 0:
            db.session.commit()
            print(f"Updated num_images for {updated_count} products")
        else:
            print("No products needed updating")

if __name__ == "__main__":
    reset_image_counts()
    print("Done!")
