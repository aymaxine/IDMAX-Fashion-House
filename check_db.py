"""
Simple script to check product and image counts in the database.
"""

from app import create_app, db
from app.models.models import Product
from app.models.product_image import ProductImage

def check_db():
    app = create_app()
    with app.app_context():
        product_count = Product.query.count()
        image_count = ProductImage.query.count()
        products_with_num_images = Product.query.filter(Product.num_images > 0).count()
        
        print(f"Total products: {product_count}")
        print(f"Products with num_images > 0: {products_with_num_images}")
        print(f"Actual image records: {image_count}")
        
        # Get a sample product
        product = Product.query.first()
        if product:
            print(f"Sample product: {product.name}, num_images: {product.num_images}")
            
            # Try to get its images
            images = list(product.images)
            print(f"Actual images: {len(images)}")

if __name__ == "__main__":
    print("Starting database check...")
    check_db()
    print("Done!")
