from flask import Blueprint, render_template, redirect, url_for, flash, abort, request, current_app
from flask_login import login_required, current_user
from app import db
from app.models.models import Product, Brand, User
from app.models.product_image import ProductImage
from app.models.order import Order, OrderItem
from app.forms import ProductForm, BrandForm
from functools import wraps
import os
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import io
import base64
from matplotlib.figure import Figure
import numpy as np
import uuid
from werkzeug.utils import secure_filename

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def save_product_image(image_file, product_id):
    """
    Save an uploaded product image to the filesystem, optimize it, create thumbnails, and return the filename.
    
    Args:
        image_file: FileStorage object from form upload
        product_id: ID of the product this image belongs to
        
    Returns:
        str: The saved filename
    """
    # Import image processing utilities
    from app.utils.image_processing import optimize_image, create_thumbnail
    
    # Create a unique filename to prevent collisions
    # Format: product_id_uuid.extension
    _, file_extension = os.path.splitext(image_file.filename)
    unique_filename = "product_{0}_{1}{2}".format(
        product_id, 
        uuid.uuid4().hex[:8],
        file_extension.lower()  # Normalize extension to lowercase
    )
    
    # Secure the filename to prevent directory traversal attacks
    filename = secure_filename(unique_filename)
    
    # Create the upload path
    upload_path = os.path.join(current_app.root_path, 'static', 'uploads', 'products')
    
    # Create directory if it doesn't exist
    if not os.path.exists(upload_path):
        os.makedirs(upload_path)
    
    # Save the file
    filepath = os.path.join(upload_path, filename)
    image_file.save(filepath)
    
    try:
        # Optimize the original image (max width 1200px)
        optimize_image(filepath, quality=85, max_size=(1200, 1200))
        
        # Create thumbnail version (200x200px)
        create_thumbnail(filepath, width=200, height=200)
        
        current_app.logger.info(f"Successfully processed image: {filename}")
    except Exception as e:
        current_app.logger.error(f"Error processing image {filename}: {str(e)}")
    
    return filename

# Function to generate charts for the admin dashboard
def generate_chart(data, chart_type, title, xlabel=None, ylabel=None, figsize=(10, 6)):
    """
    Generate a visually stunning chart using matplotlib/seaborn based on pandas data
    
    Args:
        data: pandas DataFrame or Series
        chart_type: str, type of chart ('bar', 'pie', 'line', 'area', 'heatmap', 'donut')
        title: str, title of the chart
        xlabel: str, x-axis label
        ylabel: str, y-axis label
        figsize: tuple, figure size
        
    Returns:
        str: base64 encoded image
    """
    # Use a clean style without background color
    plt.style.use('default')
    
    # Create figure with higher resolution
    fig, ax = plt.subplots(figsize=figsize, dpi=120)
    
    # Custom color palettes for different chart types
    bar_palette = sns.color_palette("viridis", n_colors=10)
    pie_palette = sns.color_palette("magma", n_colors=10)
    line_palette = sns.color_palette("plasma", n_colors=10)
    
    # Create the chart based on chart_type with enhanced styling
    if chart_type == 'bar':
        if isinstance(data, pd.DataFrame):
            # Enhanced bar chart with gradient and edge color
            bars = sns.barplot(x=data.columns[0], y=data.columns[1], data=data, ax=ax, palette=bar_palette)
            
            # Add value labels on top of each bar
            for i, bar in enumerate(bars.patches):
                bars.annotate(f'{data[data.columns[1]].iloc[i]}',
                             (bar.get_x() + bar.get_width() / 2, bar.get_height()),
                             ha='center', va='bottom', color='black', fontweight='bold', fontsize=10)
        else:
            # Add gradient effect to bars
            bars = data.plot(kind='bar', ax=ax, color=bar_palette)
            
        # Add grid for better readability
        ax.grid(axis='y', linestyle='--', alpha=0.7)
        
    elif chart_type == 'pie':
        if isinstance(data, pd.DataFrame):
            # Enhanced pie chart with shadow, explode effect, and startangle
            explode = [0.05] * len(data)  # Explode all slices slightly
            wedges, texts, autotexts = ax.pie(data[data.columns[1]], labels=data[data.columns[0]], 
                  autopct='%1.1f%%', shadow=True, startangle=90, 
                  colors=pie_palette, explode=explode, textprops={'color': 'black', 'fontweight': 'bold'})
            
            # Make percentage text larger and bold
            for autotext in autotexts:
                autotext.set_size(10)
                autotext.set_weight('bold')
        else:
            wedges, texts, autotexts = ax.pie(data.values, labels=data.index, 
                  autopct='%1.1f%%', shadow=True, startangle=90, 
                  colors=pie_palette, explode=[0.05] * len(data), 
                  textprops={'color': 'black', 'fontweight': 'bold'})
            
            for autotext in autotexts:
                autotext.set_size(10)
                autotext.set_weight('bold')
                
        ax.axis('equal')  # Equal aspect ratio ensures that pie is drawn as a circle
        
    elif chart_type == 'donut':
        # Create a donut chart (pie chart with a hole in center)
        if isinstance(data, pd.DataFrame):
            # Draw pie chart
            wedges, texts, autotexts = ax.pie(data[data.columns[1]], labels=data[data.columns[0]], 
                  autopct='%1.1f%%', startangle=90, colors=pie_palette,
                  textprops={'color': 'black', 'fontweight': 'bold'})
            
            # Make percentage text larger and bold
            for autotext in autotexts:
                autotext.set_size(10)
                autotext.set_weight('bold')
        else:
            wedges, texts, autotexts = ax.pie(data.values, labels=data.index, 
                  autopct='%1.1f%%', startangle=90, colors=pie_palette,
                  textprops={'color': 'black', 'fontweight': 'bold'})
            
        # Create the center circle to make it a donut chart
        centre_circle = plt.Circle((0, 0), 0.70, fc='white')
        ax.add_artist(centre_circle)
        
        # Add total in center
        total = sum(data[data.columns[1]]) if isinstance(data, pd.DataFrame) else sum(data.values)
        ax.text(0, 0, f'Total\n{total}', ha='center', va='center', fontsize=12, fontweight='bold', color='black')
        
        ax.axis('equal')  # Equal aspect ratio
        
    elif chart_type == 'line':
        if isinstance(data, pd.DataFrame):
            # Enhanced line plot with markers, line width and marker size
            ax = data.plot(kind='line', ax=ax, color=line_palette, marker='o', 
                         linewidth=3, markersize=8, markeredgecolor='white')
            
            # Add data point labels
            for i, val in enumerate(data[data.columns[1]]):
                ax.annotate(f'{val}', 
                          (i, val), 
                          textcoords="offset points",
                          xytext=(0, 10), 
                          ha='center', 
                          fontweight='bold',
                          color='black')
        else:
            # Enhanced line plot with markers
            ax = data.plot(kind='line', ax=ax, color=line_palette[0], marker='o', 
                         linewidth=3, markersize=8, markeredgecolor='white')
        
        # Add grid and style it
        ax.grid(linestyle='--', alpha=0.7)
        
    elif chart_type == 'area':
        # Create an area chart
        if isinstance(data, pd.DataFrame):
            ax = data.plot(kind='area', ax=ax, stacked=False, alpha=0.7)
        else:
            ax = data.plot(kind='area', ax=ax, stacked=False, alpha=0.7)
            
        # Style the area chart
        ax.grid(linestyle='--', alpha=0.5)
        ax.set_axisbelow(True)
        
    elif chart_type == 'heatmap':
        # Create correlation matrix heatmap
        if isinstance(data, pd.DataFrame) and len(data.columns) > 2:
            # Calculate correlation for numeric columns
            numeric_data = data.select_dtypes(include=[np.number])
            corr = numeric_data.corr()
            sns.heatmap(corr, annot=True, cmap='viridis', ax=ax, cbar=True,
                      linewidths=0.5, annot_kws={"size": 10, "weight": "bold"})
        else:
            # If not enough columns for correlation, create a simple heatmap
            if isinstance(data, pd.DataFrame):
                data_pivot = data.pivot(index=data.columns[0], columns=data.columns[0], values=data.columns[1])
                sns.heatmap(data_pivot, annot=True, cmap='viridis', ax=ax, cbar=True,
                          linewidths=0.5, annot_kws={"size": 10, "weight": "bold"})
            else:
                data_reshaped = data.values.reshape(-1, 1)
                sns.heatmap(data_reshaped, annot=True, cmap='viridis', ax=ax, cbar=True,
                          linewidths=0.5, annot_kws={"size": 10, "weight": "bold"})
    
    # Set title and labels with enhanced styling
    ax.set_title(title, fontsize=16, fontweight='bold', color='black', pad=20)
    if xlabel:
        ax.set_xlabel(xlabel, fontsize=12, fontweight='bold', color='black', labelpad=10)
    if ylabel:
        ax.set_ylabel(ylabel, fontsize=12, fontweight='bold', color='black', labelpad=10)
    
    # Customize tick parameters
    ax.tick_params(axis='both', colors='black', labelsize=10)
    
    # Rotate x-axis labels for better readability if it's a bar chart
    if chart_type == 'bar':
        plt.xticks(rotation=45, ha='right')
    
    # Add a subtle border around the chart
    for spine in ax.spines.values():
        spine.set_edgecolor('#555555')
        spine.set_linewidth(1.5)
    
    # Add a subtle watermark
    fig.text(0.99, 0.01, 'Fashion Catalog', fontsize=10, color='gray', ha='right', va='bottom', alpha=0.5)
    
    # Add drop shadow effect to figure
    plt.tight_layout(pad=3.0)
    
    # Save to a string buffer and convert to base64
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png', dpi=120, bbox_inches='tight', facecolor='white')
    buffer.seek(0)
    image_png = buffer.getvalue()
    buffer.close()
    
    # Encode to base64 string
    encoded = base64.b64encode(image_png)
    return 'data:image/png;base64,{}'.format(encoded.decode('utf-8'))  # Python 2.7 compatible

# Custom decorator for admin access
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/')
@login_required
@admin_required
def dashboard():
    # Basic stats
    product_count = Product.query.count()
    brand_count = Brand.query.count()
    user_count = User.query.count()
    
    # Order stats
    try:
        order_count = Order.query.count()
        processing_orders = Order.query.filter_by(status='Processing').count()
        total_revenue = db.session.query(db.func.sum(Order.total_amount)).scalar() or 0
        
        # Order status distribution for charts
        order_status_data = db.session.query(
            Order.status, 
            db.func.count(Order.id)
        ).group_by(Order.status).all()
        
        if order_status_data:
            # Create a DataFrame for the order status chart
            status_df = pd.DataFrame(order_status_data, columns=['Status', 'Count'])
            order_status_table = status_df.to_html(index=False, classes='table table-sm table-striped')
            order_status_chart = generate_chart(status_df, 'pie', 'Order Status Distribution')
            
            # Monthly revenue chart
            monthly_revenue_data = db.session.query(
                db.func.strftime('%Y-%m', Order.created_at).label('month'),
                db.func.sum(Order.total_amount).label('revenue')
            ).group_by('month').order_by('month').all()
            
            if monthly_revenue_data:
                revenue_df = pd.DataFrame(monthly_revenue_data, columns=['Month', 'Revenue'])
                monthly_revenue_chart = generate_chart(
                    revenue_df, 'line', 'Monthly Revenue', 'Month', 'Revenue (₹)')
            else:
                monthly_revenue_chart = None
        else:
            order_status_chart = None
            order_status_table = None
            monthly_revenue_chart = None
            
    except Exception as e:
        current_app.logger.error(f"Error getting order stats: {str(e)}")
        order_count = 0
        processing_orders = 0
        total_revenue = 0
        order_status_chart = None
        order_status_table = None
        monthly_revenue_chart = None
    
    # Image stats
    image_count = ProductImage.query.count()
    products_with_images = db.session.query(Product).filter(Product.num_images > 0).count()
    products_without_images = product_count - products_with_images
    
    # Latest products with images preloaded
    latest_products = Product.query.outerjoin(
        ProductImage, 
        (Product.id == ProductImage.product_id)
    ).order_by(Product.created_at.desc()).limit(5).all()
    
    # Recent users
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    # Try importing ActivityLog model (this may fail if migration hasn't been run)
    try:
        from app.models.activity_log import ActivityLog
        recent_activities = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).limit(10).all()
    except:
        recent_activities = []
    
    # Fetch all products for analytics
    products = Product.query.all()
    df = pd.DataFrame([
        {
            'gender': p.gender,
            'brand': p.brand_info.name if p.brand_info else None,
            'price': p.price,
            'created_at': p.created_at
        } for p in products
    ])
    
    # Initialize charts to None
    gender_chart = brand_chart = price_chart = monthly_chart = None
    gender_table = brand_table = price_table = None
    
    if not df.empty:
        # Gender distribution - both chart and table
        gender_counts = df['gender'].value_counts().reset_index()
        gender_counts.columns = ['Gender', 'Count']
        gender_table = gender_counts.to_html(index=False, classes='table table-sm table-striped')
        gender_chart = generate_chart(gender_counts, 'pie', 'Products by Gender')
        
        # Top brands - both chart and table
        brand_counts = df['brand'].value_counts().head(5).reset_index()
        brand_counts.columns = ['Brand', 'Count']
        brand_table = brand_counts.to_html(index=False, classes='table table-sm table-striped')
        brand_chart = generate_chart(brand_counts, 'bar', 'Top 5 Brands', 'Brand', 'Count')
        
        # Price range distribution - both chart and table
        bins = [0, 1000, 2000, 5000, 10000, float('inf')]
        labels = ['₹0-1000', '₹1000-2000', '₹2000-5000', '₹5000-10000', '₹10000+']
        df['price_range'] = pd.cut(df['price'], bins=bins, labels=labels, right=False)
        price_counts = df['price_range'].value_counts(sort=False).reset_index()
        price_counts.columns = ['Price Range', 'Count']
        price_table = price_counts.to_html(index=False, classes='table table-sm table-striped')
        price_chart = generate_chart(price_counts, 'bar', 'Price Distribution', 'Price Range', 'Count')
        
        # Monthly product additions (time series)
        try:
            # Convert created_at to datetime if needed
            if not pd.api.types.is_datetime64_any_dtype(df['created_at']):
                df['created_at'] = pd.to_datetime(df['created_at'])
            
            # Extract month and year
            df['month_year'] = df['created_at'].dt.strftime('%Y-%m')
            
            # Count products by month
            monthly_counts = df.groupby('month_year').size().reset_index(name='Count')
            monthly_counts.columns = ['Month', 'Count']
            
            # Sort by month
            monthly_counts['Month'] = pd.to_datetime(monthly_counts['Month'])
            monthly_counts = monthly_counts.sort_values('Month')
            monthly_counts['Month'] = monthly_counts['Month'].dt.strftime('%Y-%m')
            
            # Only show the last 12 months if there are many months
            if len(monthly_counts) > 12:
                monthly_counts = monthly_counts.tail(12)
                
            monthly_chart = generate_chart(monthly_counts, 'line', 'Products Added by Month', 'Month', 'Count')
        except Exception as e:
            # Using Python 2.7 compatible string formatting
            current_app.logger.error("Error creating monthly chart: {}".format(str(e)))
            monthly_chart = None
    
    # Database stats
    db_stats = {
        'last_product': Product.query.order_by(Product.created_at.desc()).first().created_at.strftime('%Y-%m-%d %H:%M') if Product.query.count() > 0 else 'N/A',
        'last_user': User.query.order_by(User.created_at.desc()).first().created_at.strftime('%Y-%m-%d %H:%M') if User.query.count() > 0 else 'N/A'
    }
    
    # Calculate database file size
    db_path = os.path.join(os.getcwd(), 'instance', 'fashion_catalog.db')
    db_size_mb = round(os.path.getsize(db_path) / (1024 * 1024), 2) if os.path.exists(db_path) else 0
    
    # Get recent orders
    try:
        recent_orders = Order.query.order_by(Order.created_at.desc()).limit(5).all()
    except:
        recent_orders = []
        
    return render_template('admin/dashboard.html', 
                           title='Admin Dashboard',
                           product_count=product_count,
                           brand_count=brand_count, 
                           user_count=user_count,
                           order_count=order_count,
                           processing_orders=processing_orders,
                           total_revenue=total_revenue,
                           image_count=image_count,
                           products_with_images=products_with_images,
                           products_without_images=products_without_images,
                           latest_products=latest_products,
                           recent_users=recent_users,
                           recent_orders=recent_orders,
                           recent_activities=recent_activities if 'recent_activities' in locals() else [],
                           # Tables (maintain backward compatibility)
                           gender_table=gender_table,
                           brand_table=brand_table,
                           price_table=price_table,
                           order_status_table=order_status_table,
                           # Charts (new)
                           gender_chart=gender_chart,
                           brand_chart=brand_chart,
                           price_chart=price_chart,
                           monthly_chart=monthly_chart,
                           order_status_chart=order_status_chart,
                           monthly_revenue_chart=monthly_revenue_chart,
                           db_stats=db_stats,
                           db_size_mb=db_size_mb)


@admin_bp.route('/products')
@login_required
@admin_required
def products():
    page = request.args.get('page', 1, type=int)
    per_page = 15
    sort_by = request.args.get('sort_by', 'created_at')
    order = request.args.get('order', 'desc')
    
    # Join with ProductImage to eagerly load images
    products_query = Product.query.outerjoin(
        ProductImage, 
        (Product.id == ProductImage.product_id)
    )
    
    # Get additional filter parameters
    status = request.args.get('status', '')
    
    # Apply status filter
    if status == 'active':
        products_query = products_query.filter(Product.active == True)
    elif status == 'inactive':
        products_query = products_query.filter(Product.active == False)
    
    # Apply sorting
    if sort_by == 'name':
        if order == 'asc':
            products_query = products_query.order_by(Product.name.asc())
        else:
            products_query = products_query.order_by(Product.name.desc())
    elif sort_by == 'price':
        if order == 'asc':
            products_query = products_query.order_by(Product.price.asc())
        else:
            products_query = products_query.order_by(Product.price.desc())
    elif sort_by == 'status':
        if order == 'asc':
            products_query = products_query.order_by(Product.active.asc())
        else:
            products_query = products_query.order_by(Product.active.desc())
    else:  # Default to created_at
        if order == 'asc':
            products_query = products_query.order_by(Product.created_at.asc())
        else:
            products_query = products_query.order_by(Product.created_at.desc())
    
    # Paginate the results
    products = products_query.paginate(page=page, per_page=per_page)
    
    # Count active and inactive products
    active_count = Product.query.filter(Product.active == True).count()
    inactive_count = Product.query.filter(Product.active == False).count()
    
    return render_template(
        'admin/products.html', 
        title='Manage Products',
        products=products,
        sort_by=sort_by,
        order=order,
        status=status,
        active_count=active_count,
        inactive_count=inactive_count
    )


@admin_bp.route('/products/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_product():
    form = ProductForm()
    form.brand_id.choices = [(b.id, b.name) for b in Brand.query.order_by('name')]
    
    if form.validate_on_submit():
        product = Product(
            product_id="PROD{0:04d}".format(Product.query.count() + 1),  # Python 2.7 compatible format
            name=form.name.data,
            brand_id=form.brand_id.data,
            gender=form.gender.data,
            price=form.price.data,
            description=form.description.data,
            primary_color=form.primary_color.data,
            num_images=0  # Will be updated if images are uploaded
        )
        db.session.add(product)
        db.session.commit()
        
        # Handle image uploads
        image_count = 0
        if form.images.data and any(form.images.data):
            for i, image_file in enumerate(form.images.data):
                if image_file.filename:
                    try:
                        # Save the image file
                        filename = save_product_image(image_file, product.id)
                        
                        # Create image record in database
                        image = ProductImage(
                            product_id=product.id,
                            filename=filename,
                            is_primary=(i == 0)  # First image is primary
                        )
                        db.session.add(image)
                        image_count += 1
                    except Exception as e:
                        current_app.logger.error("Error saving product image: {}".format(str(e)))
            
            # Update image count and save
            if image_count > 0:
                product.num_images = image_count
                db.session.commit()
        
        # Log activity
        try:
            from app.utils.logging import log_activity
            log_activity(
                action="Added new product", 
                entity_type="product", 
                entity_id=product.id, 
                details="Added product: {} with {} images".format(product.name, image_count)  # Python 2.7 compatible
            )
        except:
            # If logging functionality isn't available yet, silently continue
            pass
            
        flash('Product has been created with {} images!'.format(image_count), 'success')
        return redirect(url_for('admin.products'))
        
    return render_template('admin/product_form.html', title='New Product', form=form, legend='New Product')


@admin_bp.route('/products/<product_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_product(product_id):
    product = Product.query.filter_by(product_id=product_id).first_or_404()
    form = ProductForm()
    form.brand_id.choices = [(b.id, b.name) for b in Brand.query.order_by('name')]
    
    # Check if product exists in any orders
    from app.models.order import OrderItem
    order_count = OrderItem.query.filter_by(product_id=product.id).count()
    
    if form.validate_on_submit():
        product.name = form.name.data
        product.brand_id = form.brand_id.data
        product.gender = form.gender.data
        product.price = form.price.data
        product.description = form.description.data
        product.primary_color = form.primary_color.data
        
        # Handle image uploads
        image_count = 0
        if form.images.data and any(form.images.data):
            for i, image_file in enumerate(form.images.data):
                if image_file.filename:
                    try:
                        # Save the image file
                        filename = save_product_image(image_file, product.id)
                        
                        # Create image record in database
                        # If there are no existing images, set this as primary
                        is_primary = (i == 0 and product.num_images == 0)
                        
                        image = ProductImage(
                            product_id=product.id,
                            filename=filename,
                            is_primary=is_primary
                        )
                        db.session.add(image)
                        image_count += 1
                    except Exception as e:
                        current_app.logger.error("Error saving product image: {}".format(str(e)))
            
            # Update image count and save
            if image_count > 0:
                product.num_images += image_count
        
        db.session.commit()
        
        # Log activity
        try:
            from app.utils.logging import log_activity
            log_activity(
                action="Updated product", 
                entity_type="product", 
                entity_id=product.id, 
                details="Updated product: {} and added {} images".format(product.name, image_count)  # Python 2.7 compatible
            )
        except:
            pass
            
        flash('Your product has been updated!', 'success')
        return redirect(url_for('admin.products'))
        
    elif request.method == 'GET':
        form.name.data = product.name
        form.brand_id.data = product.brand_id
        form.gender.data = product.gender
        form.price.data = product.price
        form.description.data = product.description
        form.primary_color.data = product.primary_color
        
    return render_template('admin/product_form.html', title='Edit Product', 
                           form=form, legend='Edit Product', product=product, 
                           order_count=order_count)


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


@admin_bp.route('/products/<product_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product(product_id):
    product = Product.query.filter_by(product_id=product_id).first_or_404()
    product_name = product.name  # Save name before deletion
    
    try:
        # Check if product exists in any orders
        from app.models.order import OrderItem
        order_items = OrderItem.query.filter_by(product_id=product.id).count()
        
        if order_items > 0:
            # Instead of deleting, just mark as inactive
            product.active = False
            db.session.commit()
            
            # Log activity
            from app.utils.logging import log_activity
            log_activity(
                action="Marked product as inactive", 
                entity_type="product", 
                entity_id=product.id,
                details="Product '{}' marked as inactive because it has associated orders".format(product_name)
            )
            
            flash(f'Product "{product_name}" has been marked as inactive since it has {order_items} associated order(s).', 'warning')
            return redirect(url_for('admin.products'))
        
        # If no orders, proceed with full deletion
        
        # Delete any cart items referencing this product
        from app.models.cart import CartItem
        cart_items = CartItem.query.filter_by(product_id=product.id).all()
        for item in cart_items:
            db.session.delete(item)
        
        # Now delete the product
        db.session.delete(product)
        db.session.commit()
        
        # Log activity
        from app.utils.logging import log_activity
        log_activity(
            action="Deleted product", 
            entity_type="product", 
            details="Deleted product: {}".format(product_name)
        )
        
        flash('Your product has been deleted!', 'success')
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error deleting product: {str(e)}")
        flash(f'An error occurred while deleting the product: {str(e)}', 'danger')
    
    return redirect(url_for('admin.products'))


@admin_bp.route('/products/<product_id>/images', methods=['GET', 'POST'])
@login_required
@admin_required
def product_images(product_id):
    """View and manage product images"""
    product = Product.query.filter_by(product_id=product_id).first_or_404()
    # Explicitly call .all() to convert the AppenderQuery to a list
    images = product.images.all()
    
    # Create form for image upload from the product form
    form = ProductForm()
    form.brand_id.choices = [(b.id, b.name) for b in Brand.query.order_by('name')]
    
    if form.validate_on_submit():
        # Handle image uploads
        image_count = 0
        if form.images.data and any(form.images.data):
            for image_file in form.images.data:
                if image_file.filename:
                    try:
                        # Save the image file
                        filename = save_product_image(image_file, product.id)
                        
                        # Create image record in database
                        # If there are no existing images, set this as primary
                        is_primary = (product.num_images == 0)
                        
                        image = ProductImage(
                            product_id=product.id,
                            filename=filename,
                            is_primary=is_primary
                        )
                        db.session.add(image)
                        image_count += 1
                    except Exception as e:
                        current_app.logger.error("Error saving product image: {}".format(str(e)))
            
            # Update image count and save
            if image_count > 0:
                product.num_images += image_count
                db.session.commit()
                flash('{} images successfully uploaded.'.format(image_count), 'success')
                return redirect(url_for('admin.product_images', product_id=product_id))
    
    return render_template('admin/product_images.html', 
                           title='Product Images', 
                           product=product,
                           images=images,
                           form=form)


@admin_bp.route('/products/<product_id>/images/<int:image_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_product_image(product_id, image_id):
    """Delete a product image"""
    product = Product.query.filter_by(product_id=product_id).first_or_404()
    image = ProductImage.query.filter_by(id=image_id, product_id=product.id).first_or_404()
    
    # Get the filename to delete the actual file
    filename = image.filename
    
    # Delete from database
    db.session.delete(image)
    
    # Update product image count
    if product.num_images > 0:
        product.num_images -= 1
    
    # If the deleted image was primary, set another image as primary
    if image.is_primary and product.num_images > 0:
        # Find another image to set as primary
        another_image = ProductImage.query.filter_by(product_id=product.id).first()
        if another_image:
            another_image.is_primary = True
    
    db.session.commit()
    
    # Try to delete the file from filesystem
    try:
        from app.utils.image_processing import get_thumbnail_path
        
        # Delete original file
        file_path = os.path.join(current_app.root_path, 'static', 'uploads', 'products', filename)
        if os.path.exists(file_path):
            os.remove(file_path)
            
        # Delete thumbnail if it exists
        thumbnail_filename = get_thumbnail_path(filename)
        thumb_path = os.path.join(current_app.root_path, 'static', 'uploads', 'products', thumbnail_filename)
        if os.path.exists(thumb_path):
            os.remove(thumb_path)
    except Exception as e:
        current_app.logger.error("Error deleting image files: {}".format(str(e)))
    
    # Log activity
    try:
        from app.utils.logging import log_activity
        log_activity(
            action="Deleted product image", 
            entity_type="product", 
            entity_id=product.id, 
            details="Deleted image from product: {}".format(product.name)  # Python 2.7 compatible
        )
    except:
        pass
        
    flash('Product image has been deleted!', 'success')
    return redirect(url_for('admin.product_images', product_id=product_id))


@admin_bp.route('/products/<product_id>/images/<int:image_id>/set-primary', methods=['POST'])
@login_required
@admin_required
def set_primary_image(product_id, image_id):
    """Set an image as the primary product image"""
    product = Product.query.filter_by(product_id=product_id).first_or_404()
    image = ProductImage.query.filter_by(id=image_id, product_id=product.id).first_or_404()
    
    # Clear primary flag on all product images
    for img in ProductImage.query.filter_by(product_id=product.id).all():
        img.is_primary = False
    
    # Set the selected image as primary
    image.is_primary = True
    
    db.session.commit()
    
    # Log activity
    try:
        from app.utils.logging import log_activity
        log_activity(
            action="Set primary product image", 
            entity_type="product", 
            entity_id=product.id, 
            details="Set primary image for product: {}".format(product.name)  # Python 2.7 compatible
        )
    except:
        pass
        
    flash('Primary product image has been updated!', 'success')
    return redirect(url_for('admin.product_images', product_id=product_id))


@admin_bp.route('/brands')
@login_required
@admin_required
def brands():
    brands = Brand.query.all()
    return render_template('admin/brands.html', title='Manage Brands', brands=brands)


@admin_bp.route('/brands/new', methods=['GET', 'POST'])
@login_required
@admin_required
def new_brand():
    form = BrandForm()
    if form.validate_on_submit():
        brand = Brand(name=form.name.data, description=form.description.data)
        db.session.add(brand)
        db.session.commit()
        
        # Log activity
        try:
            from app.utils.logging import log_activity
            log_activity(
                action="Added new brand", 
                entity_type="brand", 
                entity_id=brand.id, 
                details="Added brand: {}".format(brand.name)  # Python 2.7 compatible
            )
        except:
            pass
            
        flash('Brand has been created!', 'success')
        return redirect(url_for('admin.brands'))
        
    return render_template('admin/brand_form.html', title='New Brand', form=form, legend='New Brand')


@admin_bp.route('/brands/<int:brand_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_brand(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    form = BrandForm()
    
    if form.validate_on_submit():
        brand.name = form.name.data
        brand.description = form.description.data
        db.session.commit()
        
        # Log activity
        try:
            from app.utils.logging import log_activity
            log_activity(
                action="Updated brand", 
                entity_type="brand", 
                entity_id=brand.id, 
                details="Updated brand: {}".format(brand.name)  # Python 2.7 compatible
            )
        except:
            pass
            
        flash('Brand has been updated!', 'success')
        return redirect(url_for('admin.brands'))
        
    elif request.method == 'GET':
        form.name.data = brand.name
        form.description.data = brand.description
        
    return render_template('admin/brand_form.html', title='Edit Brand', 
                           form=form, legend='Edit Brand')


@admin_bp.route('/brands/<int:brand_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_brand(brand_id):
    brand = Brand.query.get_or_404(brand_id)
    
    # Check if brand has products
    if brand.products.count() > 0:
        flash('Cannot delete brand with associated products.', 'danger')
        return redirect(url_for('admin.brands'))
    
    brand_name = brand.name  # Save name before deletion
    db.session.delete(brand)
    db.session.commit()
    
    # Log activity
    try:
        from app.utils.logging import log_activity
        log_activity(
            action="Deleted brand", 
            entity_type="brand", 
            details="Deleted brand: {}".format(brand_name)  # Python 2.7 compatible
        )
    except:
        pass
        
    flash('Brand has been deleted!', 'success')
    return redirect(url_for('admin.brands'))


@admin_bp.route('/users')
@login_required
@admin_required
def users():
    users = User.query.all()
    return render_template('admin/users.html', title='Manage Users', users=users)


@admin_bp.route('/users/<int:user_id>/toggle-admin', methods=['POST'])
@login_required
@admin_required
def toggle_admin(user_id):
    user = User.query.get_or_404(user_id)
    
    # Prevent removing admin rights from yourself
    if user.id == current_user.id:
        flash('You cannot remove your own admin rights.', 'danger')
    else:
        user.is_admin = not user.is_admin
        db.session.commit()
        
        # Log activity
        try:
            from app.utils.logging import log_activity
            log_activity(
                action="Changed user admin status", 
                entity_type="user", 
                entity_id=user.id, 
                details="{} admin rights for {}".format('Granted' if user.is_admin else 'Revoked', user.username)  # Python 2.7 compatible
            )
        except:
            pass
            
        status = 'granted' if user.is_admin else 'revoked'
        flash('Admin rights {} for {}.'.format(status, user.username), 'success')  # Python 2.7 compatible
    
    return redirect(url_for('admin.users'))


# Redirect routes for backward compatibility
@admin_bp.route('/products/add')
@login_required
@admin_required
def add_product():
    """Redirect to new_product for backward compatibility"""
    return redirect(url_for('admin.new_product'))


@admin_bp.route('/brands/add')
@login_required
@admin_required
def add_brand():
    """Redirect to new_brand for backward compatibility"""
    return redirect(url_for('admin.new_brand'))


@admin_bp.route('/backup-db')
@login_required
@admin_required
def backup_database():
    """Create a backup of the database"""
    try:
        import shutil
        from datetime import datetime
        
        # Source database file
        source_db = os.path.join(os.getcwd(), 'instance', 'fashion_catalog.db')
        
        # Create backups directory if it doesn't exist
        backup_dir = os.path.join(os.getcwd(), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        # Target backup file with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = os.path.join(backup_dir, 'fashion_catalog_backup_{}.db'.format(timestamp))  # Python 2.7 compatible
        
        # Copy the database file
        shutil.copy2(source_db, backup_file)
        
        # Log activity
        try:
            from app.utils.logging import log_activity
            log_activity(
                action="Database backup", 
                details="Created database backup: {}".format(os.path.basename(backup_file))  # Python 2.7 compatible
            )
        except:
            pass
        
        flash('Database backup created successfully: {}'.format(os.path.basename(backup_file)), 'success')  # Python 2.7 compatible
    except Exception as e:
        flash('Error creating database backup: {}'.format(str(e)), 'danger')  # Python 2.7 compatible
    
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/activity-log')
@login_required
@admin_required
def activity_log():
    """View the activity log"""
    try:
        from app.models.activity_log import ActivityLog
        
        page = request.args.get('page', 1, type=int)
        logs = ActivityLog.query.order_by(ActivityLog.timestamp.desc()).paginate(page=page, per_page=20)
        
        return render_template('admin/activity_log.html', 
                               title='Activity Log',
                               logs=logs)
    except:
        flash('Activity log functionality is not available. Please run database migrations.', 'warning')
        return redirect(url_for('admin.dashboard'))
