from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.order import Order, OrderItem
from app.models.models import User
from app.routes.admin import admin_required
from app.utils.email import send_email
from app.utils.logging import log_activity

admin_orders_bp = Blueprint('admin_orders', __name__, url_prefix='/admin/orders')

@admin_orders_bp.route('/')
@login_required
@admin_required
def manage_orders():
    """View and manage all orders"""
    page = request.args.get('page', 1, type=int)
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    per_page = 20
    
    # Start with base query
    query = Order.query
    
    # Apply filters
    if status:
        query = query.filter_by(status=status)
    
    if search:
        query = query.filter(
            (Order.order_number.like(f'%{search}%')) |
            (Order.full_name.like(f'%{search}%')) |
            (Order.email.like(f'%{search}%'))
        )
    
    # Apply ordering
    query = query.order_by(Order.created_at.desc())
    
    # Paginate
    orders = query.paginate(page=page, per_page=per_page)
    
    # Get stats
    total_orders = Order.query.count()
    processing_orders = Order.query.filter_by(status='Processing').count()
    total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
    
    return render_template(
        'admin/manage_orders.html',
        title='Manage Orders',
        orders=orders,
        total_orders=total_orders,
        processing_orders=processing_orders,
        total_revenue=total_revenue,
        status=status,
        search=search
    )


@admin_orders_bp.route('/<int:order_id>')
@login_required
@admin_required
def order_details(order_id):
    """View details of a specific order"""
    order = Order.query.get_or_404(order_id)
    
    # Get status color
    status_colors = {
        'Processing': 'info',
        'Shipped': 'primary',
        'Delivered': 'success',
        'Cancelled': 'danger'
    }
    status_color = status_colors.get(order.status, 'secondary')
    
    # Get user order stats
    user_order_count = Order.query.filter_by(user_id=order.user_id).count()
    user_total_spent = db.session.query(db.func.sum(Order.total_amount)).filter_by(user_id=order.user_id).scalar() or 0
    
    return render_template(
        'admin/order_details.html',
        title=f'Order {order.order_number}',
        order=order,
        status_color=status_color,
        user_order_count=user_order_count,
        user_total_spent=user_total_spent
    )


@admin_orders_bp.route('/<int:order_id>/update-status', methods=['GET', 'POST'])
@login_required
@admin_required
def update_order_status(order_id):
    """Update the status of an order"""
    order = Order.query.get_or_404(order_id)
    
    if request.method == 'POST':
        status = request.form.get('status')
        notes = request.form.get('notes', '')
        notify_customer = bool(request.form.get('notify_customer', False))
        
        # Update order status
        old_status = order.status
        order.status = status
        db.session.commit()
        
        # Log activity
        try:
            log_activity(
                action="Updated order status",
                entity_type="order",
                entity_id=order.id,
                details=f"Updated order {order.order_number} status from {old_status} to {status}"
            )
        except Exception as e:
            current_app.logger.error(f"Failed to log activity: {str(e)}")
        
        # Notify customer if requested
        if notify_customer:
            try:
                subject = f"Your Order Status: {order.order_number}"
                html_content = f"""
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h1 style="color: #4CAF50; text-align: center;">Order Status Update</h1>
                    <p>Dear {order.full_name},</p>
                    <p>Your order status has been updated to <strong>{status}</strong>.</p>
                    <div style="background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px;">
                        <h3 style="margin-top: 0;">Order Details</h3>
                        <p><strong>Order Number:</strong> {order.order_number}</p>
                        <p><strong>Order Date:</strong> {order.created_at.strftime('%B %d, %Y')}</p>
                        <p><strong>Total Amount:</strong> ₹{order.total_amount:.2f}</p>
                    </div>
                """
                
                if notes:
                    html_content += f"<p><strong>Additional Notes:</strong> {notes}</p>"
                
                html_content += """
                    <p>Thank you for shopping with us!</p>
                    <p>The Fashion Catalog Team</p>
                    
                    <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #777; font-size: 12px;">
                        <p>This is an automated message, please do not reply to this email.</p>
                        <p>© 2025 Fashion Catalog. All rights reserved.</p>
                    </div>
                </div>
                """
                
                send_email(order.email, subject, html_content)
                flash(f"Customer notified about status change to {status}", "info")
            except Exception as e:
                current_app.logger.error(f"Failed to send status notification email: {str(e)}")
        
        flash(f"Order status updated to {status}", "success")
        return redirect(url_for('admin_orders.order_details', order_id=order.id))
    else:
        # Handle GET request (direct link update)
        status = request.args.get('status')
        if status:
            old_status = order.status
            order.status = status
            db.session.commit()
            
            flash(f"Order status updated to {status}", "success")
        
        return redirect(url_for('admin_orders.order_details', order_id=order.id))


@admin_orders_bp.route('/customer/<int:user_id>')
@login_required
@admin_required
def customer_profile(user_id):
    """View customer profile and order history"""
    user = User.query.get_or_404(user_id)
    
    # Get all orders for this customer
    orders = Order.query.filter_by(user_id=user_id).order_by(Order.created_at.desc()).all()
    
    # Calculate statistics
    total_orders = len(orders)
    total_spent = sum(order.total_amount for order in orders)
    
    # Get status statistics
    status_counts = {}
    for order in orders:
        if order.status in status_counts:
            status_counts[order.status] += 1
        else:
            status_counts[order.status] = 1
    
    return render_template(
        'admin/customer_profile.html',
        title=f'Customer Profile - {user.username}',
        user=user,
        orders=orders,
        total_orders=total_orders,
        total_spent=total_spent,
        status_counts=status_counts
    )
