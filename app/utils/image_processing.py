"""
Image processing utilities for the Fashion Catalog application.

This module provides functions for handling image operations like resizing,
creating thumbnails, and optimizing images.
"""

import os
from PIL import Image
from flask import current_app
import logging

logger = logging.getLogger(__name__)

def get_product_images(product, convert_to_list=True):
    """
    Helper function to safely get product images, handling AppenderQuery issues.
    
    Args:
        product: The product object
        convert_to_list: Whether to convert AppenderQuery to list
        
    Returns:
        list: List of product images or empty list if none exists
    """
    if not product:
        return []
    
    # Try-except blocks to avoid using hasattr() which causes issues in Jinja
    try:
        # Check if images are already preloaded
        if product.images_list is not None:
            return product.images_list
    except (AttributeError, TypeError):
        pass
    
    try:
        # Try to access the images relationship
        if convert_to_list:
            images = product.images.all()
            return images if images else []
        else:
            return product.images
    except (AttributeError, TypeError):
        return []

def create_thumbnail(source_path, width=200, height=200):
    """
    Create a thumbnail version of an image with a specified width and height.
    
    Args:
        source_path (str): Path to the source image
        width (int): Desired thumbnail width
        height (int): Desired thumbnail height
        
    Returns:
        str: Path to the created thumbnail or None if creation failed
    """
    try:
        # Validate source path
        if not os.path.exists(source_path):
            logger.error(f"Source image not found: {source_path}")
            return None
            
        # Get directory and filename
        directory, filename = os.path.split(source_path)
        name, extension = os.path.splitext(filename)
        
        # Create thumbnail filename
        thumbnail_filename = f"{name}_thumb{extension}"
        thumbnail_path = os.path.join(directory, thumbnail_filename)
        
        # Open image and create thumbnail
        with Image.open(source_path) as img:
            # Create a white background for transparent images
            if img.mode in ('RGBA', 'LA'):
                try:
                    background = Image.new(img.mode[:-1], img.size, (255, 255, 255))
                    background.paste(img, img.split()[-1])
                    img = background
                except Exception as e:
                    logger.warning(f"Error handling transparent image: {str(e)}")
                    # Continue with original image if background creation fails
            
            # Resize image to fit within width x height while maintaining aspect ratio
            img.thumbnail((width, height), Image.LANCZOS)
            
            # Save the thumbnail
            img.save(thumbnail_path, quality=85, optimize=True)
            
            return thumbnail_filename
    except Exception as e:
        logger.error(f"Error creating thumbnail for {source_path}: {str(e)}")
        return None

def optimize_image(source_path, quality=85, max_size=None):
    """
    Optimize an image by reducing its file size.
    
    Args:
        source_path (str): Path to the source image
        quality (int): Quality of the optimized image (1-100)
        max_size (tuple): Maximum width and height (optional)
        
    Returns:
        bool: True if optimization succeeded, False otherwise
    """
    try:
        with Image.open(source_path) as img:
            # Resize if max_size is specified
            if max_size and (img.width > max_size[0] or img.height > max_size[1]):
                img.thumbnail(max_size, Image.LANCZOS)
            
            # Save with optimization
            img.save(source_path, quality=quality, optimize=True)
            
            return True
    except Exception as e:
        logger.error(f"Error optimizing image {source_path}: {str(e)}")
        return False

def get_thumbnail_path(original_filename):
    """
    Get the thumbnail path for a given original image filename.
    
    Args:
        original_filename (str): Original image filename
        
    Returns:
        str: Thumbnail filename
    """
    if not original_filename:
        return None
        
    try:
        name, extension = os.path.splitext(original_filename)
        return f"{name}_thumb{extension}"
    except Exception as e:
        logger.error(f"Error creating thumbnail path for {original_filename}: {str(e)}")
        return original_filename  # Fall back to the original filename
