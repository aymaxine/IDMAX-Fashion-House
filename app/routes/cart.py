from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import current_user, login_required
from app import db
from app.models.models import Product
from app.models.cart import CartItem
from sqlalchemy.exc import SQLAlchemyError

cart_bp = Blueprint('cart', __name__, url_prefix='/cart')

@cart_bp.route('/')
@login_required
def view_cart():
    """
    View the current user's shopping cart
    """
    # Get all cart items for the current user with their associated products
    cart_items = CartItem.query.filter_by(user_id=current_user.id).join(
        Product, CartItem.product_id == Product.id
    ).with_entities(
        CartItem.id, 
        CartItem.quantity, 
        Product.id.label('product_id'),
        Product.product_id.label('product_code'),
        Product.name, 
        Product.price,
        Product.primary_color
    ).all()
    
    # Calculate total price
    total_price = sum(item.price * item.quantity for item in cart_items)
    item_count = sum(item.quantity for item in cart_items)
    
    return render_template(
        'cart/view.html', 
        cart_items=cart_items, 
        total_price=total_price, 
        item_count=item_count
    )

@cart_bp.route('/add/<product_id>', methods=['POST'])
@login_required
def add_to_cart(product_id):
    """
    Add a product to the cart
    """
    # Get the product
    product = Product.query.filter_by(product_id=product_id).first_or_404()
    
    # Get quantity from form, default to 1
    quantity = int(request.form.get('quantity', 1))
    
    # Check if the item is already in the cart
    cart_item = CartItem.query.filter_by(
        user_id=current_user.id, 
        product_id=product.id
    ).first()
    
    try:
        if cart_item:
            # Update quantity if it already exists
            cart_item.quantity += quantity
            db.session.commit()
            flash(f'Updated quantity of {product.name} in your cart.', 'success')
        else:
            # Create a new cart item
            cart_item = CartItem(
                user_id=current_user.id,
                product_id=product.id,
                quantity=quantity
            )
            db.session.add(cart_item)
            db.session.commit()
            flash(f'Added {product.name} to your cart!', 'success')
            
        # Return to the product page or wherever the user came from
        return redirect(request.referrer or url_for('products.product_detail', product_id=product_id))
    except SQLAlchemyError as e:
        db.session.rollback()
        flash('An error occurred while adding the item to your cart.', 'danger')
        return redirect(url_for('products.product_detail', product_id=product_id))

@cart_bp.route('/update/<int:item_id>', methods=['POST'])
@login_required
def update_cart_item(item_id):
    """
    Update the quantity of a cart item
    """
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    quantity = int(request.form.get('quantity', 1))
    
    if quantity <= 0:
        # Remove the item if quantity is 0 or less
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from your cart.', 'info')
    else:
        # Update the quantity
        cart_item.quantity = quantity
        db.session.commit()
        flash('Cart updated successfully.', 'success')
    
    # If AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
    
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/remove/<int:item_id>', methods=['POST'])
@login_required
def remove_from_cart(item_id):
    """
    Remove an item from the cart
    """
    cart_item = CartItem.query.filter_by(id=item_id, user_id=current_user.id).first_or_404()
    
    try:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Item removed from your cart.', 'success')
    except SQLAlchemyError:
        db.session.rollback()
        flash('An error occurred while removing the item.', 'danger')
    
    # If AJAX request, return JSON response
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({'success': True})
        
    return redirect(url_for('cart.view_cart'))

@cart_bp.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    """
    Checkout process for the cart
    """
    # Get all cart items for the current user with their associated products
    cart_items = CartItem.query.filter_by(user_id=current_user.id).join(
        Product, CartItem.product_id == Product.id
    ).with_entities(
        CartItem.id, 
        CartItem.quantity, 
        Product.id.label('product_id'),
        Product.product_id.label('product_code'),
        Product.name, 
        Product.price,
        Product.primary_color
    ).all()
    
    # Calculate total price
    total_price = sum(item.price * item.quantity for item in cart_items)
    item_count = sum(item.quantity for item in cart_items)
    
    # Check if cart is empty
    if not cart_items:
        flash('Your cart is empty. Add some products before checking out.', 'warning')
        return redirect(url_for('cart.view_cart'))
    
    # Handle form submission    if request.method == 'POST':
        # Here you would typically process payment, create order, etc.
        # For now, just show a success message and clear the cart
        
        # Clear the user's cart
        CartItem.query.filter_by(user_id=current_user.id).delete()
        db.session.commit()
        
        # Redirect to order success page
        return render_template('cart/order_success.html')
    
    return render_template(
        'cart/checkout.html', 
        cart_items=cart_items, 
        total_price=total_price, 
        item_count=item_count
    )
