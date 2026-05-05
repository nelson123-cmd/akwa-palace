import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import Config
from typing import Dict, Tuple

class EmailService:
    """Email service for sending confirmations"""
    
    def __init__(self):
        self.smtp_host = Config.SMTP_HOST
        self.smtp_port = Config.SMTP_PORT
        self.smtp_user = Config.SMTP_USER
        self.smtp_password = Config.SMTP_PASSWORD
        self.from_email = Config.SMTP_FROM
    
    def send_booking_confirmation(self, booking_data: Dict, booking_reference: str) -> Tuple[bool, str]:
        """Send booking confirmation email to client"""
        try:
            # Create email content
            subject = f"Booking Confirmation - Akwa Palace (#{booking_reference})"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ padding: 30px; background: #f9f9f9; }}
                    .room-details {{ background: white; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #e67e22; }}
                    .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                    .button {{ display: inline-block; padding: 12px 24px; background: #e67e22; color: white; text-decoration: none; border-radius: 5px; margin-top: 20px; }}
                    .highlight {{ color: #e67e22; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏨 Akwa Palace</h1>
                        <p>Booking Confirmation</p>
                    </div>
                    <div class="content">
                        <h2>Dear {booking_data['full_name']},</h2>
                        <p>Thank you for choosing Akwa Palace! Your booking has been received and is being processed.</p>
                        
                        <div class="room-details">
                            <h3>Booking Details</h3>
                            <p><strong>Booking Reference:</strong> <span class="highlight">{booking_reference}</span></p>
                            <p><strong>Room:</strong> {booking_data['selected_room']['name']}</p>
                            <p><strong>Check-in Date:</strong> {booking_data['check_in_date']}</p>
                            <p><strong>Duration:</strong> {booking_data['duration_stay']} night(s)</p>
                            <p><strong>Number of Persons:</strong> {booking_data['number_persons']}</p>
                            <p><strong>Total Price:</strong> <span class="highlight">{booking_data['total_price']:,.2f} XAF</span></p>
                        </div>
                        
                        <div class="room-details">
                            <h3>Room Features</h3>
                            <p><strong>View:</strong> {booking_data['selected_room']['view']}</p>
                            <p><strong>Size:</strong> {booking_data['selected_room']['size']}</p>
                            <p><strong>Bedding:</strong> {booking_data['selected_room']['bedding']}</p>
                        </div>
                        
                        <p>We will contact you shortly to confirm your reservation. If you have any questions, please don't hesitate to contact us.</p>
                        
                        <div style="text-align: center;">
                            <a href="https://akwa-palace.com" class="button">Visit Our Website</a>
                        </div>
                    </div>
                    <div class="footer">
                        <p>Akwa Palace - Luxury Redefined</p>
                        <p>Email: info@akwa-palace.com | Phone: +237 XXX XXX XXX</p>
                        <p>&copy; 2025 Akwa Palace. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
            Akwa Palace - Booking Confirmation (#{booking_reference})
            
            Dear {booking_data['full_name']},
            
            Thank you for choosing Akwa Palace! Your booking has been received.
            
            Booking Details:
            - Booking Reference: {booking_reference}
            - Room: {booking_data['selected_room']['name']}
            - Check-in Date: {booking_data['check_in_date']}
            - Duration: {booking_data['duration_stay']} night(s)
            - Number of Persons: {booking_data['number_persons']}
            - Total Price: {booking_data['total_price']:,.2f} XAF
            
            Room Features:
            - View: {booking_data['selected_room']['view']}
            - Size: {booking_data['selected_room']['size']}
            - Bedding: {booking_data['selected_room']['bedding']}
            
            We will contact you shortly to confirm your reservation.
            
            Best regards,
            Akwa Palace Team
            """
            
            # Send email
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = booking_data['email_address']
            
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True, "Email sent successfully"
            
        except Exception as e:
            return False, str(e)
    
    def send_admin_notification(self, booking_data: Dict, booking_reference: str) -> Tuple[bool, str]:
        """Send notification email to admin"""
        try:
            subject = f"New Booking Alert - {booking_reference}"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: #e67e22; color: white; padding: 20px; text-align: center; }}
                    .content {{ padding: 20px; background: #f9f9f9; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h2>New Booking Received!</h2>
                    </div>
                    <div class="content">
                        <p><strong>Client:</strong> {booking_data['full_name']}</p>
                        <p><strong>Email:</strong> {booking_data['email_address']}</p>
                        <p><strong>Phone:</strong> {booking_data['phone_number']}</p>
                        <p><strong>Room:</strong> {booking_data['selected_room']['name']}</p>
                        <p><strong>Check-in:</strong> {booking_data['check_in_date']}</p>
                        <p><strong>Reference:</strong> {booking_reference}</p>
                        <p><strong>Total:</strong> {booking_data['total_price']:,.2f} XAF</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = Config.ADMIN_EMAIL
            
            part1 = MIMEText(html_content, 'html')
            msg.attach(part1)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True, "Admin notification sent"
            
        except Exception as e:
            return False, str(e)

class Validator:
    """Input validation and sanitization"""
    
    @staticmethod
    def validate_booking_data(data: Dict) -> Tuple[bool, str]:
        """Validate booking form data"""
        
        # Required fields check
        required_fields = ['full_name', 'phone_number', 'email_address', 'country', 
                          'duration_stay', 'check_in_date', 'number_persons', 'selected_room']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Missing required field: {field}"
        
        # Full name validation
        name = data['full_name'].strip()
        if len(name) < 2 or len(name) > Config.MAX_NAME_LENGTH:
            return False, "Full name must be between 2 and 100 characters"
        if not re.match(r'^[a-zA-Z\s\-\']+$', name):
            return False, "Full name can only contain letters, spaces, hyphens, and apostrophes"
        
        # Phone number validation
        phone = data['phone_number'].strip()
        if not re.match(r'^[+]?[\d\s\-\(\)]{8,20}$', phone):
            return False, "Invalid phone number format"
        
        # Email validation
        email = data['email_address'].strip()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False, "Invalid email address format"
        if len(email) > Config.MAX_EMAIL_LENGTH:
            return False, "Email address is too long"
        
        # Country validation
        country = data['country'].strip()
        if len(country) < 2 or len(country) > Config.MAX_COUNTRY_LENGTH:
            return False, "Invalid country"
        
        # Duration validation
        try:
            duration = int(data['duration_stay'])
            if not (Config.MIN_DURATION_DAYS <= duration <= Config.MAX_DURATION_DAYS):
                return False, f"Duration must be between {Config.MIN_DURATION_DAYS} and {Config.MAX_DURATION_DAYS} days"
        except ValueError:
            return False, "Invalid duration value"
        
        # Check-in date validation
        try:
            check_in = datetime.strptime(data['check_in_date'], '%Y-%m-%d')
            if check_in < datetime.now():
                return False, "Check-in date must be in the future"
        except ValueError:
            return False, "Invalid date format"
        
        # Number of persons validation
        try:
            persons = int(data['number_persons'])
            if not (Config.MIN_PERSONS <= persons <= Config.MAX_PERSONS):
                return False, f"Number of persons must be between {Config.MIN_PERSONS} and {Config.MAX_PERSONS}"
        except ValueError:
            return False, "Invalid number of persons"
        
        # Special requests sanitization (if present)
        if 'special_requests' in data and data['special_requests']:
            import re
            cleaned = re.sub(r'<[^>]+>', '', data['special_requests'])
            if len(cleaned) > 1000:
                return False, "Special requests are too long"
            data['special_requests'] = cleaned
        
        # Selected room validation
        room = data['selected_room']
        if not isinstance(room, dict):
            return False, "Invalid room data"
        if 'name' not in room or 'price' not in room:
            return False, "Invalid room information"
        
        return True, "Validation passed"
    
    @staticmethod
    def sanitize_input(text: str) -> str:
        """Sanitize user input"""
        if not text:
            return ""
        return bleach.clean(text.strip(), strip=True)

# Initialize services
email_service = EmailService()
validator = Validator()
import smtplib
import re
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime
from config import Config
from typing import Dict, Tuple

class EmailService:
    """Email service for sending confirmations"""
    
    def __init__(self):
        self.smtp_host = Config.SMTP_HOST
        self.smtp_port = Config.SMTP_PORT
        self.smtp_user = Config.SMTP_USER
        self.smtp_password = Config.SMTP_PASSWORD
        self.from_email = Config.SMTP_FROM
    
    def send_booking_confirmation(self, booking_data: Dict, booking_reference: str) -> Tuple[bool, str]:
        """Send booking confirmation email to client"""
        try:
            subject = f"Booking Confirmation - Akwa Palace (#{booking_reference})"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ padding: 30px; background: #f9f9f9; }}
                    .room-details {{ background: white; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 4px solid #e67e22; }}
                    .footer {{ text-align: center; padding: 20px; font-size: 12px; color: #666; }}
                    .highlight {{ color: #e67e22; font-weight: bold; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🏨 Akwa Palace</h1>
                        <p>Booking Confirmation</p>
                    </div>
                    <div class="content">
                        <h2>Dear {booking_data['full_name']},</h2>
                        <p>Thank you for choosing Akwa Palace! Your booking has been received and is being processed.</p>
                        <div class="room-details">
                            <h3>Booking Details</h3>
                            <p><strong>Booking Reference:</strong> <span class="highlight">{booking_reference}</span></p>
                            <p><strong>Room:</strong> {booking_data['selected_room']['name']}</p>
                            <p><strong>Check-in Date:</strong> {booking_data['check_in_date']}</p>
                            <p><strong>Duration:</strong> {booking_data['duration_stay']} night(s)</p>
                            <p><strong>Number of Persons:</strong> {booking_data['number_persons']}</p>
                            <p><strong>Total Price:</strong> <span class="highlight">{booking_data['total_price']:,.2f} XAF</span></p>
                        </div>
                        <p>We will contact you shortly to confirm your reservation.</p>
                    </div>
                    <div class="footer">
                        <p>Akwa Palace - Luxury Redefined</p>
                        <p>&copy; 2025 Akwa Palace. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            text_content = f"""
Akwa Palace - Booking Confirmation (#{booking_reference})

Dear {booking_data['full_name']},

Thank you for choosing Akwa Palace! Your booking has been received.

Booking Details:
- Booking Reference: {booking_reference}
- Room: {booking_data['selected_room']['name']}
- Check-in Date: {booking_data['check_in_date']}
- Duration: {booking_data['duration_stay']} night(s)
- Number of Persons: {booking_data['number_persons']}
- Total Price: {booking_data['total_price']:,.2f} XAF

We will contact you shortly to confirm your reservation.

Best regards,
Akwa Palace Team
"""
            
            if not all([self.smtp_user, self.smtp_password, self.smtp_host]):
                print("📧 Email not configured - skipping (demo mode)")
                return True, "Email not configured (demo mode)"
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = booking_data['email_address']
            
            part1 = MIMEText(text_content, 'plain')
            part2 = MIMEText(html_content, 'html')
            
            msg.attach(part1)
            msg.attach(part2)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True, "Email sent successfully"
            
        except Exception as e:
            print(f"Email error: {str(e)}")
            return False, str(e)
    
    def send_admin_notification(self, booking_data: Dict, booking_reference: str) -> Tuple[bool, str]:
        """Send notification email to admin"""
        try:
            subject = f"New Booking Alert - {booking_reference}"
            
            html_content = f"""
            <h2>New Booking Received!</h2>
            <p><strong>Client:</strong> {booking_data['full_name']}</p>
            <p><strong>Email:</strong> {booking_data['email_address']}</p>
            <p><strong>Phone:</strong> {booking_data['phone_number']}</p>
            <p><strong>Room:</strong> {booking_data['selected_room']['name']}</p>
            <p><strong>Check-in:</strong> {booking_data['check_in_date']}</p>
            <p><strong>Reference:</strong> {booking_reference}</p>
            <p><strong>Total:</strong> {booking_data['total_price']:,.2f} XAF</p>
            """
            
            if not Config.ADMIN_EMAIL or Config.ADMIN_EMAIL == 'admin@akwa-palace.com':
                return True, "Admin email not configured"
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.from_email
            msg['To'] = Config.ADMIN_EMAIL
            
            part1 = MIMEText(html_content, 'html')
            msg.attach(part1)
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.send_message(msg)
            
            return True, "Admin notification sent"
            
        except Exception as e:
            print(f"Admin email error: {str(e)}")
            return False, str(e)

class Validator:
    """Input validation and sanitization"""
    
    @staticmethod
    def validate_booking_data(data: Dict) -> Tuple[bool, str]:
        """Validate booking form data"""
        
        required_fields = ['full_name', 'phone_number', 'email_address', 'country', 
                          'duration_stay', 'check_in_date', 'number_persons', 'selected_room']
        
        for field in required_fields:
            if field not in data or not data[field]:
                return False, f"Missing required field: {field}"
        
        # Full name validation
        name = data['full_name'].strip()
        if len(name) < 2 or len(name) > 100:
            return False, "Full name must be between 2 and 100 characters"
        if not re.match(r'^[a-zA-Z\s\-\']+$', name):
            return False, "Full name can only contain letters, spaces, hyphens, and apostrophes"
        
        # Phone number validation
        phone = data['phone_number'].strip()
        if not re.match(r'^[+]?[\d\s\-\(\)]{8,20}$', phone):
            return False, "Invalid phone number format"
        
        # Email validation
        email = data['email_address'].strip()
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            return False, "Invalid email address format"
        if len(email) > 100:
            return False, "Email address is too long"
        
        # Country validation
        country = data['country'].strip()
        if len(country) < 2 or len(country) > 50:
            return False, "Invalid country"
        
        # Duration validation
        try:
            duration = int(data['duration_stay'])
            if not (1 <= duration <= 365):
                return False, "Duration must be between 1 and 365 days"
        except ValueError:
            return False, "Invalid duration value"
        
        # Check-in date validation
        try:
            check_in = datetime.strptime(data['check_in_date'], '%Y-%m-%d')
            if check_in < datetime.now():
                return False, "Check-in date must be in the future"
        except ValueError:
            return False, "Invalid date format"
        
        # Number of persons validation
        try:
            persons = int(data['number_persons'])
            if not (1 <= persons <= 10):
                return False, "Number of persons must be between 1 and 10"
        except ValueError:
            return False, "Invalid number of persons"
        
        # Special requests sanitization
        if 'special_requests' in data and data['special_requests']:
            cleaned = re.sub(r'<[^>]+>', '', data['special_requests'])
            if len(cleaned) > 500:
                return False, "Special requests are too long"
            data['special_requests'] = cleaned
        
        # Selected room validation
        room = data['selected_room']
        if not isinstance(room, dict):
            return False, "Invalid room data"
        if 'name' not in room or 'price' not in room:
            return False, "Invalid room information"
        
        return True, "Validation passed"

# Initialize services
email_service = EmailService()
validator = Validator()
