"""
Create the necessary directories for product image uploads
"""
import os

def create_uploads_directory():
    """Create the uploads directory for product images"""
    # Determine the path to the uploads directory
    base_dir = os.path.abspath(os.path.dirname(__file__))
    uploads_dir = os.path.join(base_dir, 'app', 'static', 'uploads')
    products_dir = os.path.join(uploads_dir, 'products')
    
    # Create directories if they don't exist
    if not os.path.exists(uploads_dir):
        print("Creating uploads directory...")
        os.makedirs(uploads_dir)
        print(f"Created directory: {uploads_dir}")
    
    if not os.path.exists(products_dir):
        print("Creating products uploads directory...")
        os.makedirs(products_dir)
        print(f"Created directory: {products_dir}")
    
    print("Upload directories setup complete!")

if __name__ == '__main__':
    create_uploads_directory()
