from sqlalchemy import func
from app.models.models import Product, Brand
from app.models.product_image import ProductImage
from app import db

def get_filtered_products(page=1, per_page=12, gender=None, brand_id=None, color=None, min_price=None, max_price=None, featured_only=False):
    """
    Helper function to get filtered products with consistent logic across routes
    
    Args:
        page (int): Current page number
        per_page (int): Number of items per page
        gender (str, optional): Filter by gender
        brand_id (int, optional): Filter by brand ID
        color (str, optional): Filter by primary color
        min_price (float, optional): Minimum price filter
        max_price (float, optional): Maximum price filter
        featured_only (bool, optional): If True, only return featured products
        
    Returns:
        tuple: (
            products (Pagination object), 
            brands (list), 
            colors (list), 
            genders (list), 
            price_stats (object)
        )
    """
    # Import get_product_images helper to ensure consistent image handling
    from app.utils.image_processing import get_product_images
      # Start with base query - we'll handle image loading after pagination
    # since Product.images uses lazy='dynamic' which doesn't support joinedload
    query = Product.query
    
    # Always filter by active status for regular users
    # Only show active products
    query = query.filter(Product.active == True)
    
    # Apply filters if provided
    if gender:
        query = query.filter(Product.gender == gender)
    if brand_id:
        query = query.filter(Product.brand_id == brand_id)
    if color:
        query = query.filter(Product.primary_color == color)
    if min_price:
        query = query.filter(Product.price >= min_price)
    if max_price:
        query = query.filter(Product.price <= max_price)
        
    # If featured only is requested, filter by featured flag or use the newest products
    if featured_only:
        # If you have a featured field, use that
        if hasattr(Product, 'featured'):
            query = query.filter(Product.featured == True)
        # Otherwise, just get the newest products
        else:
            query = query.order_by(Product.created_at.desc())    # Get paginated products
    products = query.order_by(Product.id).paginate(page=page, per_page=per_page, error_out=False)
    
    # Preload images for each product to prevent AppenderQuery issues
    # Since the images relationship uses lazy='dynamic', we need to call .all() for each product
    for product in products.items:
        # Manually load and attach images to prevent repeated queries in templates
        product.images_list = product.images.all()
    
    # Get all brands for the filter
    brands = Brand.query.order_by(Brand.name).all()
    
    # Get distinct colors for the filter
    colors = db.session.query(Product.primary_color).distinct().order_by(Product.primary_color).all()
    colors = [color[0] for color in colors if color[0]]  # Extract color names and remove None values
    
    # Get gender options
    genders = db.session.query(Product.gender).distinct().order_by(Product.gender).all()
    genders = [gender[0] for gender in genders if gender[0]]  # Extract gender options
    
    # Get price range
    price_stats = db.session.query(
        func.min(Product.price).label('min_price'),
        func.max(Product.price).label('max_price')
    ).one()
    
    return products, brands, colors, genders, price_stats
