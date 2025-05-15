from flask import Blueprint, render_template, redirect, url_for, flash, request, session, current_app
from flask_login import login_required, current_user
from app import db
from app.models.cart import CartItem
from app.models.order import Order, OrderItem
from app.models.models import Product
import uuid
import datetime
from app.utils.logging import log_activity
from app.utils.email import send_order_confirmation

orders_bp = Blueprint('orders', __name__, url_prefix='/orders')


@orders_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """
    Handle the checkout process
    """
    # Get cart items
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Your cart is empty', 'warning')
        return redirect(url_for('cart.view_cart'))
    
    # Calculate cart total
    total = sum(item.quantity * item.product.price for item in cart_items)
    
    if request.method == 'POST':
        # Create unique order number
        order_number = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        # Create order
        order = Order(
            order_number=order_number,
            user_id=current_user.id,
            full_name=request.form.get('full_name'),
            email=request.form.get('email'),
            address=request.form.get('address'),
            city=request.form.get('city'),
            state=request.form.get('state'),
            postal_code=request.form.get('postal_code'),
            country=request.form.get('country'),
            phone=request.form.get('phone'),
            total_amount=total,
            payment_method=request.form.get('payment_method', 'Credit Card'),
            payment_status='Paid'  # For simplicity, assume payment was successful
        )
        
        db.session.add(order)
        
        # Create order items
        for cart_item in cart_items:
            order_item = OrderItem(
                order=order,
                product_id=cart_item.product_id,
                quantity=cart_item.quantity,
                price=cart_item.product.price  # Store current price
            )
            db.session.add(order_item)
          # Clear the cart
        for item in cart_items:
            db.session.delete(item)
        
        # Commit all changes
        try:
            db.session.commit()
            
            # Log activity
            log_activity(
                action="Placed order",
                entity_type="order",
                entity_id=order.id,
                details=f"Order {order.order_number} for ${order.total_amount:.2f}"
            )
            
            # Send confirmation email
            send_order_confirmation(order)
            
            # Store order number for success page
            session['last_order_number'] = order.order_number
            
            # Redirect to success page
            return redirect(url_for('orders.order_success'))
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Order creation failed: {str(e)}")
            flash('An error occurred while processing your order. Please try again.', 'danger')
    
    # Render checkout page
    return render_template(
        'orders/checkout.html',
        title='Checkout',
        cart_items=cart_items,
        total=total
    )


@orders_bp.route('/success')
@login_required
def order_success():
    """
    Display order success page
    """
    order_number = session.get('last_order_number')
    
    if not order_number:
        flash('No recent order found', 'warning')
        return redirect(url_for('main.index'))
    
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    
    # Only allow the order owner to view this page
    if order.user_id != current_user.id:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.index'))
    
    # Get product categories from the order
    ordered_products = [item.product for item in order.items]
    ordered_brands = [product.brand_id for product in ordered_products if product.brand_id]
    ordered_genders = [product.gender for product in ordered_products if product.gender]
    
    # Find similar products based on brand and gender
    recommended_products = Product.query.filter(
        (Product.brand_id.in_(ordered_brands) | Product.gender.in_(ordered_genders)) &
        (Product.id.notin_([p.id for p in ordered_products]))
    ).order_by(db.func.random()).limit(4).all()
    
    # If not enough recommendations, add some random products
    if len(recommended_products) < 4:
        existing_ids = [p.id for p in recommended_products] + [p.id for p in ordered_products]
        additional_products = Product.query.filter(
            Product.id.notin_(existing_ids)
        ).order_by(db.func.random()).limit(4 - len(recommended_products)).all()
        
        recommended_products.extend(additional_products)
    
    # Clear the session variable to prevent refresh issues
    session.pop('last_order_number', None)
    
    # Create activity log entry for recommendations
    try:
        log_activity(
            action="Product recommendations",
            entity_type="order",
            entity_id=order.id,
            details=f"Showed {len(recommended_products)} product recommendations"
        )
    except Exception as e:
        current_app.logger.error(f"Failed to log recommendations: {str(e)}")
    
    return render_template(
        'orders/order_success.html',
        title='Order Confirmation',
        order=order,
        recommended_products=recommended_products
    )


@orders_bp.route('/history')
@login_required
def order_history():
    """
    Display order history for the current user
    """
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    
    return render_template(
        'orders/order_history.html',
        title='Order History',
        orders=orders
    )


@orders_bp.route('/view/<order_number>')
@login_required
def view_order(order_number):
    """
    View details of a specific order
    """
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    
    # Only allow the order owner to view this page
    if order.user_id != current_user.id and not current_user.is_admin:
        flash('Unauthorized access', 'danger')
        return redirect(url_for('main.index'))
    
    return render_template(
        'orders/order_detail.html',
        title=f'Order {order.order_number}',
        order=order
    )
