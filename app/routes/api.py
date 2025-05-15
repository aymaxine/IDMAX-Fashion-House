from flask import Blueprint, jsonify, request
from app.models.models import Product
from sqlalchemy import or_
from app.utils.filters import get_filtered_products

api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/products', methods=['GET'])
def get_products():
    """
    API endpoint for getting products with pagination and filtering.
    Used for lazy loading on the homepage.
    """
    # Get page number from query parameters
    page = request.args.get('page', 1, type=int)
    per_page = 8  # Number of products per page
    
    # Get filter parameters
    gender = request.args.get('gender')
    brand_id = request.args.get('brand_id', type=int)
    color = request.args.get('color')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    featured_only = request.args.get('featured', 'false').lower() == 'true'
    
    # Use the helper function to get filtered products
    products, _, _, _, _ = get_filtered_products(
        page=page,
        per_page=per_page,
        gender=gender,
        brand_id=brand_id,
        color=color,
        min_price=min_price,
        max_price=max_price,
        featured_only=featured_only
    )
    
    # Format products for API response
    products_data = []
    for product in products.items:
        products_data.append({
            'product_id': product.product_id,
            'name': product.name,
            'brand_name': product.brand_info.name,
            'brand_id': product.brand_id,
            'primary_color': product.primary_color,
            'gender': product.gender,
            'price': float(product.price),
            'image_url': product.image_url if hasattr(product, 'image_url') else None
        })
    
    return jsonify({
        'products': products_data,
        'current_page': products.page,
        'total_pages': products.pages,
        'has_next': products.has_next,
        'has_prev': products.has_prev
    })

@api_bp.route('/search', methods=['GET'])
def search_products():
    """
    API endpoint for searching products
    """
    query = request.args.get('query', '')
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Number of products per page
    
    if not query:
        return jsonify({'products': [], 'error': 'No search query provided'})
    
    # Search in product name, description and color
    search_query = Product.query.filter(
        or_(
            Product.name.ilike(f'%{query}%'),
            Product.description.ilike(f'%{query}%'),
            Product.primary_color.ilike(f'%{query}%')
        )
    ).order_by(Product.created_at.desc())
    
    # Paginate the results
    search_results = search_query.paginate(page=page, per_page=per_page)
    
    # Format products for API response
    products_data = []
    for product in search_results.items:
        products_data.append({
            'product_id': product.product_id,
            'name': product.name,
            'brand_name': product.brand_info.name,
            'brand_id': product.brand_id,
            'primary_color': product.primary_color,
            'gender': product.gender,
            'price': float(product.price),
            'image_url': product.image_url if hasattr(product, 'image_url') else None
        })
    
    return jsonify({
        'products': products_data,
        'query': query,
        'current_page': search_results.page,
        'total_pages': search_results.pages,
        'has_next': search_results.has_next,
        'has_prev': search_results.has_prev
    })
