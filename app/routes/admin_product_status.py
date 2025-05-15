from flask import current_app, flash, redirect, url_for
from flask_login import login_required
from app.models import Product
from app.extensions import db
from app.routes import admin_bp
from app.utils.decorators import admin_required

@admin_bp.route('/products/<product_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_product_status(product_id):
    """Toggle a product's active status"""
    product = Product.query.filter_by(product_id=product_id).first_or_404()
    
    # Toggle the active status
    product.active = not product.active
    db.session.commit()
    
    # Log activity
    try:
        from app.utils.logging import log_activity
        status = "activated" if product.active else "deactivated"
        log_activity(
            action=f"Product {status}",
            entity_type="product",
            entity_id=product.id,
            details=f"Product '{product.name}' has been {status}"
        )
    except Exception as e:
        current_app.logger.error(f"Error logging product status change: {str(e)}")
    
    if product.active:
        flash(f"Product '{product.name}' has been activated and is now visible to customers.", "success")
    else:
        flash(f"Product '{product.name}' has been deactivated and is now hidden from customers.", "warning")
    
    return redirect(url_for('admin.products'))
