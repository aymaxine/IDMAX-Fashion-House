from flask import Blueprint, render_template, request
from app.models.models import Brand, Product
from app.models.product_image import ProductImage
from sqlalchemy import func
from app import db

brands_bp = Blueprint('brands', __name__, url_prefix='/brands')

@brands_bp.route('/')
def brand_list():
    """
    View function for the brands list page
    """
    # Get all brands with product count
    brands_with_counts = db.session.query(
        Brand,
        func.count(Product.id).label('product_count')
    ).outerjoin(Product).group_by(Brand.id).all()
    
    return render_template('brand_list.html', brands=brands_with_counts)

@brands_bp.route('/<int:brand_id>')
def brand_detail(brand_id):
    """
    View function for the brand detail page
    """
    # Get the brand or return 404
    brand = Brand.query.get_or_404(brand_id)
      # Get products for this brand, with pagination and preloaded images
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Join with product images to preload them
    products_query = Product.query.outerjoin(
        ProductImage, 
        (Product.id == ProductImage.product_id)
    ).filter(Product.brand_id == brand_id)
    
    products = products_query.paginate(page=page, per_page=per_page)
    
    # Get gender distribution for this brand
    gender_distribution = db.session.query(
        Product.gender, 
        func.count(Product.id)
    ).filter_by(brand_id=brand_id).group_by(Product.gender).all()
    
    # Get color distribution for this brand
    color_distribution = db.session.query(
        Product.primary_color, 
        func.count(Product.id)
    ).filter_by(brand_id=brand_id).group_by(Product.primary_color).all()
    
    # Get price statistics for this brand
    price_stats = db.session.query(
        func.min(Product.price).label('min_price'),
        func.max(Product.price).label('max_price'),
        func.avg(Product.price).label('avg_price')
    ).filter_by(brand_id=brand_id).one()
    
    return render_template(
        'brand_detail.html',
        brand=brand,
        products=products,
        gender_distribution=gender_distribution,
        color_distribution=color_distribution,
        price_stats=price_stats
    )
