from app import create_app, db
from app.models.models import Product, Brand

app = create_app()
with app.app_context():
    product_count = Product.query.count()
    brand_count = Brand.query.count()
    print(f"Database contains {product_count} products and {brand_count} brands")
    
    if product_count > 0:
        # Check if products have images
        products_with_images = Product.query.filter(Product.num_images > 0).count()
        print(f"Products with images: {products_with_images}")
        
        # Get a sample of products
        sample_products = Product.query.limit(5).all()
        print("\nSample products:")
        for prod in sample_products:
            print(f"ID: {prod.product_id}, Name: {prod.name}, Brand: {prod.brand_id}, Images: {prod.num_images}")
