from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from app.forms import ContactForm, NewsletterForm

static_pages_bp = Blueprint('static_pages', __name__)

@static_pages_bp.route('/about')
def about():
    """
    View function for the About page
    """
    return render_template('static_pages/about.html', title='About Us')


@static_pages_bp.route('/contact', methods=['GET', 'POST'])
def contact():
    """
    View function for the Contact page
    """
    form = ContactForm()
    if form.validate_on_submit():
        # In a real application, you would process the form data here
        # For example, send an email or store the message in a database
        flash('Your message has been sent! We will get back to you soon.', 'success')
        return redirect(url_for('static_pages.contact'))
        
    return render_template('static_pages/contact.html', title='Contact Us', form=form)


@static_pages_bp.route('/newsletter', methods=['POST'])
def newsletter():
    """
    View function for processing newsletter subscriptions
    """
    # For JSON requests from the frontend script
    if request.is_json:
        data = request.get_json()
        email = data.get('email', '')
        
        # In a real application, you would validate the email and save it to a database
        # For now, we'll just return a success message
        if email:
            # Here you would typically add the email to your newsletter database
            return jsonify({'success': True, 'message': 'Successfully subscribed to the newsletter!'})
        else:
            return jsonify({'success': False, 'message': 'Email is required'})
            
    # For form submissions without JavaScript
    form = NewsletterForm()
    if form.validate_on_submit():
        # In a real application, you would save the email to a database
        flash('Thank you for subscribing to our newsletter!', 'success')
        return redirect(url_for('main.index'))
        
    # If form validation fails
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{error}", 'danger')
    return redirect(url_for('main.index'))
