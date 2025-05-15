#!/usr/bin/env python
"""
Generate thumbnails for all existing product images in the database.
This script should be run after implementing the thumbnail functionality
to create thumbnails for images that were uploaded before the feature was added.
"""
import os
import sys
from app import create_app
from app.utils.image_processing import create_thumbnail, optimize_image

def generate_thumbnails():
    """
    Generate thumbnails for all existing product images
    """
    app = create_app()
    
    with app.app_context():
        # Get the path to the product images directory
        uploads_path = os.path.join(app.root_path, 'static', 'uploads', 'products')
        
        if not os.path.exists(uploads_path):
            print("Product uploads directory not found.")
            sys.exit(1)
            
        # Get all image files in the directory
        files = [f for f in os.listdir(uploads_path) 
                if os.path.isfile(os.path.join(uploads_path, f)) 
                and not f.endswith('_thumb.jpg') 
                and not f.endswith('_thumb.png')
                and not f.endswith('_thumb.jpeg')
                and not f.endswith('_thumb.gif')]
        
        if not files:
            print("No product images found.")
            return
            
        print(f"Found {len(files)} product images. Generating thumbnails...")
        
        # Create thumbnails and optimize images
        success_count = 0
        for filename in files:
            filepath = os.path.join(uploads_path, filename)
            try:
                # Optimize the original image
                optimize_image(filepath, quality=85, max_size=(1200, 1200))
                
                # Create thumbnail version
                thumbnail = create_thumbnail(filepath, width=200, height=200)
                if thumbnail:
                    success_count += 1
                    print(f"Created thumbnail for {filename}")
                else:
                    print(f"Failed to create thumbnail for {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {str(e)}")
                
        print(f"Completed. Successfully generated {success_count} thumbnails out of {len(files)} images.")

if __name__ == '__main__':
    generate_thumbnails()
