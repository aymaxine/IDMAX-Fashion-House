from flask import Blueprint, render_template, redirect, url_for, flash, session, request
from app.models.models import Product
from app import db

compare_bp = Blueprint('compare', __name__, url_prefix='/compare')

MAX_COMPARE_ITEMS = 4  # Maximum number of items to compare

@compare_bp.route('/add/<int:product_id>', methods=['POST'])
def add_to_compare(product_id):
    product = Product.query.get_or_404(product_id)
    compare_list = session.get('compare_list', [])

    if product.id not in compare_list:
        if len(compare_list) < MAX_COMPARE_ITEMS:
            compare_list.append(product.id)
            session['compare_list'] = compare_list
            flash(f'{product.name} added to comparison list.', 'success')
        else:
            flash(f'Comparison list is full (max {MAX_COMPARE_ITEMS} items).', 'warning')
    else:
        flash(f'{product.name} is already in the comparison list.', 'info')

    return redirect(request.referrer or url_for('main.index'))

@compare_bp.route('/')
def view_compare():
    compare_ids = session.get('compare_list', [])
    products_to_compare = []
    if compare_ids:
        # Preserve order of addition
        products_to_compare = Product.query.filter(Product.id.in_(compare_ids)).all()
        # Sort them based on the order in compare_ids
        products_to_compare.sort(key=lambda p: compare_ids.index(p.id))
        
    return render_template('compare/view.html', products=products_to_compare, title="Compare Products")

@compare_bp.route('/remove/<int:product_id>', methods=['POST'])
def remove_from_compare(product_id):
    product = Product.query.get_or_404(product_id)
    compare_list = session.get('compare_list', [])

    if product.id in compare_list:
        compare_list.remove(product.id)
        session['compare_list'] = compare_list
        flash(f'{product.name} removed from comparison list.', 'success')
    else:
        flash(f'{product.name} was not in the comparison list.', 'info')
    
    return redirect(url_for('compare.view_compare'))

@compare_bp.route('/clear', methods=['POST'])
def clear_compare():
    if 'compare_list' in session:
        session.pop('compare_list')
        flash('Comparison list cleared.', 'success')
    else:
        flash('Comparison list was already empty.', 'info')
        
    return redirect(url_for('compare.view_compare'))
