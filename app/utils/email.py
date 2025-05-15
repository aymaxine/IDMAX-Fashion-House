from flask import current_app
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

def send_email(to_email, subject, html_content):
    """
    Send an email using the app's email configuration
    
    Args:
        to_email: Recipient email address
        subject: Email subject
        html_content: HTML content of the email
        
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    # This is a mock implementation for the demo app
    # In a real app, you would use a real email service
    try:
        current_app.logger.info(f"EMAIL NOTIFICATION - To: {to_email}, Subject: {subject}")
        current_app.logger.debug(f"Email content: {html_content}")
        
        # For demo purposes, we're just logging instead of actually sending
        return True
        
        # Real implementation would be something like:
        # smtp_server = current_app.config.get('MAIL_SERVER')
        # smtp_port = current_app.config.get('MAIL_PORT')
        # smtp_username = current_app.config.get('MAIL_USERNAME')
        # smtp_password = current_app.config.get('MAIL_PASSWORD')
        # sender_email = current_app.config.get('MAIL_DEFAULT_SENDER')
        # 
        # msg = MIMEMultipart('alternative')
        # msg['Subject'] = subject
        # msg['From'] = sender_email
        # msg['To'] = to_email
        # msg.attach(MIMEText(html_content, 'html'))
        # 
        # with smtplib.SMTP(smtp_server, smtp_port) as server:
        #     server.starttls()
        #     server.login(smtp_username, smtp_password)
        #     server.send_message(msg)
        #     return True
        
    except Exception as e:
        current_app.logger.error(f"Failed to send email: {str(e)}")
        return False
        
def send_order_confirmation(order):
    """
    Send an order confirmation email
    
    Args:
        order: Order object
    
    Returns:
        bool: True if email sent successfully, False otherwise
    """
    subject = f"Order Confirmation - {order.order_number}"
    
    # Build the HTML content
    items_html = ""
    for item in order.items:
        items_html += f"""
        <tr>
            <td>{item.product.name}</td>
            <td>{item.quantity}</td>
            <td>₹{item.price:.2f}</td>
            <td>₹{(item.price * item.quantity):.2f}</td>
        </tr>
        """
    
    html_content = f"""
    <html>
    <body>
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <h1 style="color: #4CAF50; text-align: center;">Order Confirmation</h1>
            <p>Dear {order.full_name},</p>
            <p>Thank you for your order! We're pleased to confirm that we've received your order.</p>
            
            <div style="background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <h3 style="margin-top: 0;">Order Details</h3>
                <p><strong>Order Number:</strong> {order.order_number}</p>
                <p><strong>Order Date:</strong> {order.created_at.strftime('%B %d, %Y at %H:%M')}</p>
                <p><strong>Payment Method:</strong> {order.payment_method}</p>
                <p><strong>Status:</strong> {order.status}</p>
            </div>
            
            <h3>Order Items</h3>
            <table style="width: 100%; border-collapse: collapse;">
                <thead style="background-color: #f2f2f2;">
                    <tr>
                        <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Product</th>
                        <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Quantity</th>
                        <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Price</th>
                        <th style="padding: 8px; text-align: left; border-bottom: 1px solid #ddd;">Total</th>
                    </tr>
                </thead>
                <tbody>
                    {items_html}
                    <tr>
                        <td colspan="3" style="padding: 8px; text-align: right; border-top: 2px solid #ddd;"><strong>Total:</strong></td>
                        <td style="padding: 8px; border-top: 2px solid #ddd;"><strong>₹{order.total_amount:.2f}</strong></td>
                    </tr>
                </tbody>
            </table>
            
            <div style="background-color: #f8f9fa; padding: 15px; margin: 20px 0; border-radius: 5px;">
                <h3 style="margin-top: 0;">Shipping Details</h3>
                <p>{order.address}</p>
                <p>{order.city}, {order.state} {order.postal_code}</p>
                <p>{order.country}</p>
                <p>Phone: {order.phone}</p>
            </div>
            
            <p style="margin-top: 30px;">If you have any questions about your order, please contact our customer service at support@fashion-catalog.com.</p>
            
            <p>Thank you for shopping with us!</p>
            <p>The Fashion Catalog Team</p>
            
            <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee; color: #777; font-size: 12px;">
                <p>This is an automated message, please do not reply to this email.</p>
                <p>© 2025 Fashion Catalog. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    return send_email(order.email, subject, html_content)
