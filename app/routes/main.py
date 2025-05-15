from flask import Blueprint, render_template, request, current_app, jsonify, redirect, url_for, flash
from sqlalchemy import func, or_, and_
from app.models.models import Product, Brand
from app.utils.filters import get_filtered_products
from app import db
from flask_login import current_user, login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/admin-dashboard')
@login_required
def admin_dashboard_redirect():
    """
    Redirects to the admin dashboard if the user is an admin,
    otherwise redirects to the home page with an error message.
    """
    if current_user.is_admin:
        return redirect(url_for('admin.dashboard'))
    else:
        flash('You do not have admin privileges.', 'danger')
        return redirect(url_for('main.index'))

@main_bp.route('/api/check-admin')
@login_required
def check_admin():
    """API endpoint that returns JSON with the user's admin status"""
    return jsonify({
        'is_admin': current_user.is_admin,
        'username': current_user.username
    })

@main_bp.route('/admin')
def admin_router():
    """
    Smart router for admin access:
    - If user is authenticated and has admin rights, redirects to the admin dashboard
    - If user is authenticated but not an admin, shows an error message and redirects to home
    - If user is not authenticated, redirects to login page with a next parameter
    """
    if current_user.is_authenticated:
        if current_user.is_admin:
            return redirect(url_for('admin.dashboard'))
        else:
            flash('You do not have administrative privileges to access that page.', 'danger')
            return redirect(url_for('main.index'))
    else:
        # Not logged in - redirect to login page with next parameter set to admin dashboard
        return redirect(url_for('auth.login', next=url_for('admin.dashboard')))

@main_bp.route('/')
def index():
    # Get page number from query parameters
    page = request.args.get('page', 1, type=int)
    per_page = 8  # Reduced number of products for homepage
    
    # Get filter parameters
    gender = request.args.get('gender')
    brand_id = request.args.get('brand_id', type=int)
    color = request.args.get('color')
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    
    # Import helper functions
    from app.utils.image_processing import get_product_images
    
    # Use the helper function to get filtered products
    # Set featured_only=True to get featured/newest products for homepage
    products, brands, colors, genders, price_stats = get_filtered_products(
        page=page,
        per_page=per_page,
        gender=gender,
        brand_id=brand_id,
        color=color,
        min_price=min_price,
        max_price=max_price,
        featured_only=True
    )
    
    # Eagerly load all product images to prevent AppenderQuery issues
    for product in products.items:
        product.images_list = get_product_images(product)
    
    # Statistics for display
    total_products = Product.query.count()
    total_brands = Brand.query.count()
    
    return render_template(
        'index.html', 
        products=products,
        brands=brands,
        colors=colors,
        genders=genders,
        price_stats=price_stats,
        total_products=total_products,
        total_brands=total_brands,
        selected_gender=gender,
        selected_brand_id=brand_id,
        selected_color=color,
        selected_min_price=min_price,
        selected_max_price=max_price
    )
    
@main_bp.route('/search')
def search():
    """
    View function for searching products by keyword
    """
    # Get search query and other parameters
    query = request.args.get('query', '').strip()
    page = request.args.get('page', 1, type=int)
    per_page = 12  # Number of products per page
    sort = request.args.get('sort', 'relevance')  # Options: relevance, price_low, price_high, newest
    
    if query:
        # Search terms
        search_terms = [term.strip() for term in query.split() if term.strip()]
        
        # Build search query
        search_filter = []
        
        # Add search conditions for each term to improve relevance
        for term in search_terms:
            term_filter = or_(
                Product.name.ilike(f'%{term}%'),
                Product.description.ilike(f'%{term}%'),
                Product.primary_color.ilike(f'%{term}%'),
                Product.product_id.ilike(f'%{term}%')
            )
            search_filter.append(term_filter)
        
        # Combine all term filters with AND
        product_query = Product.query.filter(and_(*search_filter) if search_filter else True)
        
        # Apply sorting
        if sort == 'price_low':
            product_query = product_query.order_by(Product.price.asc())
        elif sort == 'price_high':
            product_query = product_query.order_by(Product.price.desc())
        elif sort == 'newest':
            product_query = product_query.order_by(Product.created_at.desc())
        else:  # Default to relevance - exact matches in name first
            # This orders exact matches in the name field higher
            # For a more sophisticated relevance ranking, consider using full-text search
            product_query = product_query.order_by(
                # Exact matches in product_id come first
                ~(func.lower(Product.product_id) == query.lower()),
                # Exact matches in name come next
                ~(func.lower(Product.name) == query.lower()),
                # Then by name containing the query
                ~(Product.name.ilike(f'%{query}%')),
                # Finally by created date (newest first)
                Product.created_at.desc()
            )
            
        # Paginate the results
        search_results = product_query.paginate(page=page, per_page=per_page, error_out=False)
          # Also search for matching brands to display
        # Search terms for brands
        brand_search_terms = [term.strip() for term in query.split() if term.strip()]
        brand_filters = []
        
        # Add search conditions for each term
        for term in brand_search_terms:
            term_filter = or_(
                Brand.name.ilike(f'%{term}%'),
                Brand.description.ilike(f'%{term}%')
            )
            brand_filters.append(term_filter)
              # Combine with OR to find brands matching any term
        matching_brands = Brand.query.filter(or_(*brand_filters)).order_by(Brand.name).limit(8).all()
        
        # Ensure no None descriptions to prevent template issues
        for brand in matching_brands:
            if brand.description is None:
                brand.description = ""
          # Get additional filtered products data
        _, brands, colors, genders, price_stats = get_filtered_products(page=1, per_page=1)
        
        # Ensure no None descriptions in these brands too
        for brand in brands:
            if brand.description is None:
                brand.description = ""
        
        # Get total count of results for display
        total_results = search_results.total
        
        # Import product image helper
        from app.utils.image_processing import get_product_images
          # Preload images for each product to prevent lazy loading issues
        for product in search_results.items:
            product.images_list = get_product_images(product)
            
        return render_template(
            'search_results.html',
            title=f'Search Results for "{query}"',
            query=query,
            products=search_results,
            brands=matching_brands,
            colors=colors,
            genders=genders,
            price_stats=price_stats,
            total_results=total_results,
            sort=sort
        )    
    else:
        # Empty search, provide default values
        return render_template(
            'search_results.html', 
            title='Search', 
            query='', 
            products=None,
            brands=None,
            total_results=0,
            sort='relevance'
        )
