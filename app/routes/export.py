import csv
import io
from datetime import datetime
from flask import Blueprint, Response, make_response, current_app
from flask_login import login_required, current_user
from app.models.models import Product, Brand, User
from app.routes.admin import admin_required

export_bp = Blueprint('export', __name__)

@export_bp.route('/export-products-csv')
@login_required
@admin_required
def export_products():
    """Export all products to CSV file"""
    # Create a string buffer
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header row
    writer.writerow([
        'ID', 'Product ID', 'Name', 'Brand ID', 'Brand Name', 
        'Gender', 'Price', 'Color', 'Description', 'Created Date', 'Updated Date'
    ])
    
    # Query products with brand info
    products = Product.query.all()
    
    # Write data rows
    for product in products:
        writer.writerow([
            product.id,
            product.product_id,
            product.name,
            product.brand_id,
            product.brand_info.name if product.brand_info else '',
            product.gender,
            product.price,
            product.primary_color,
            product.description,
            product.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            product.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Create a response to download the file
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename=products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response

@export_bp.route('/export-brands-csv')
@login_required
@admin_required
def export_brands():
    """Export all brands to CSV file"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header row
    writer.writerow([
        'ID', 'Name', 'Description', 'Product Count', 
        'Created Date', 'Updated Date'
    ])
    
    # Query brands
    brands = Brand.query.all()
    
    # Write data rows
    for brand in brands:
        writer.writerow([
            brand.id,
            brand.name,
            brand.description,
            brand.products.count(),
            brand.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            brand.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Create a response to download the file
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename=brands_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response

@export_bp.route('/export-users-csv')
@login_required
@admin_required
def export_users():
    """Export all users to CSV file"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write header row
    writer.writerow([
        'ID', 'Username', 'Email', 'Is Admin', 'Created Date'
    ])
    
    # Query users
    users = User.query.all()
    
    # Write data rows
    for user in users:
        writer.writerow([
            user.id,
            user.username,
            user.email,
            'Yes' if user.is_admin else 'No',
            user.created_at.strftime('%Y-%m-%d %H:%M:%S')
        ])
    
    # Create a response to download the file
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = f"attachment; filename=users_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    response.headers["Content-type"] = "text/csv"
    
    return response
