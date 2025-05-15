from flask import Blueprint, render_template, abort, request
from app.models.models import Product, Brand
from app.models.product_image import ProductImage
from app.utils.filters import get_filtered_products
from sqlalchemy import func
from app import db

products_bp = Blueprint('products', __name__, url_prefix='/products')

@products_bp.route('/')
def product_list():
    """
    View function for products list with filtering
    """
    # Get page number from query parameters
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Number of products per page
    
    # Get filter parameters
    gender = request.args.get('gender')
    brand_id = request.args.get('brand_id', type=int)
    color = request.args.get('color')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
      # Import helper functions
    from app.utils.image_processing import get_product_images
      # Use the helper function to get filtered products
    products, brands, colors, genders, price_stats = get_filtered_products(
        page=page,
        per_page=per_page,
        gender=gender,
        brand_id=brand_id,
        color=color,
        min_price=min_price,
        max_price=max_price
    )
    
    # Preload images for each product in the pagination
    for product in products.items:
        product.images_list = get_product_images(product)
    
    return render_template(
        'product_list.html',
        products=products,
        brands=brands,
        colors=colors,
        genders=genders,
        price_stats=price_stats,
        selected_gender=gender,
        selected_brand_id=brand_id,
        selected_color=color,
        selected_min_price=min_price,
        selected_max_price=max_price
    )

@products_bp.route('/<product_id>')
def product_detail(product_id):
    """
    View function for the product detail page
    """
    product = Product.query.filter_by(product_id=product_id).first_or_404()
    
    # Import image processing utilities
    from app.utils.image_processing import get_product_images
    
    # Use the helper function to get product images safely
    product_images = get_product_images(product)
    
    # Get related products (same brand, same gender)
    related_products = Product.query.filter(
        Product.brand_id == product.brand_id,
        Product.gender == product.gender,
        Product.product_id != product.product_id
    ).limit(4).all()
    
    # Get price statistics for this brand
    price_stats = db.session.query(
        func.min(Product.price).label('min_price'),
        func.max(Product.price).label('max_price'),
        func.avg(Product.price).label('avg_price')
    ).filter(Product.brand_id == product.brand_id).one()
    
    # Get count of products in this brand
    brand_product_count = Product.query.filter_by(brand_id=product.brand_id).count()    # Get count of products with same color
    if product.primary_color:
        color_product_count = Product.query.filter_by(primary_color=product.primary_color).count()
    else:
        color_product_count = Product.query.filter(Product.primary_color.is_(None)).count()
    
    return render_template(
        'product_detail.html',
        product=product,
        product_images=product_images if 'product_images' in locals() else [],
        related_products=related_products,
        price_stats=price_stats,
        brand_product_count=brand_product_count,
        color_product_count=color_product_count
    )

@products_bp.route('/search')
def search():
    """
    Search function for products, brands, and users
    """
    query = request.args.get('q', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    if not query:
        return render_template('search_results.html', 
                              title='Search Results',
                              query='',
                              products=[],
                              brands=[],
                              total_results=0)
      # Search in products with images preloaded
    product_results = Product.query.outerjoin(
        ProductImage, 
        (Product.id == ProductImage.product_id)
    ).filter(
        (Product.name.ilike(f'%{query}%')) | 
        (Product.description.ilike(f'%{query}%')) |
        (Product.gender.ilike(f'%{query}%')) |
        (Product.primary_color.ilike(f'%{query}%'))
    ).paginate(page=page, per_page=per_page)
    
    # Search in brands
    brand_results = Brand.query.filter(
        (Brand.name.ilike(f'%{query}%')) |
        (Brand.description.ilike(f'%{query}%'))
    ).all()
    
    total_results = product_results.total + len(brand_results)
    
    return render_template('search_results.html',
                          title=f'Search Results for "{query}"',
                          query=query,
                          products=product_results,
                          brands=brand_results,
                          total_results=total_results)