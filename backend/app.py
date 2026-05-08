from flask import Flask, request, jsonify
from flask_cors import CORS
from config import config, Config
from models import db
from utils import email_service, validator
from middleware import rate_limit, validate_json, security_headers, sanitize_data
import os
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)

# Get environment
env = os.getenv('FLASK_ENV', 'production')
app.config.from_object(config.get(env, config['default']))

# Configure CORS
CORS(app, origins=[
    'https://akwapalace.vercel.app',     
    'https://akwapalace.pythonanywhere.com',
    'http://localhost:5000',
    'http://127.0.0.1:5500'
], supports_credentials=True, methods=["GET", "POST", "OPTIONS", "PUT", "DELETE"], allow_headers=["Content-Type", "Authorization"])

# Apply security headers to all responses
app.after_request(security_headers)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'success': True,
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'environment': app.config['FLASK_ENV']
    })

@app.route('/api/book', methods=['POST'])
@rate_limit(limit_per_hour=Config.RATE_LIMIT)
@validate_json(required_fields=['full_name', 'phone_number', 'email_address', 'country', 
                                 'duration_stay', 'check_in_date', 'number_persons', 'selected_room'])
def create_booking():
    """
    Create a new booking
    Expects JSON payload with booking details
    """
    try:
        data = request.get_json()
        
        # Validate all input data
        is_valid, validation_message = validator.validate_booking_data(data)
        if not is_valid:
            return jsonify({
                'success': False,
                'message': validation_message
            }), 400
        
        # Calculate total price
        total_price = data['selected_room']['price'] * data['duration_stay']
        data['total_price'] = total_price
        
        # Create booking in database
        result = db.create_booking(data)
        
        if not result['success']:
            return jsonify({
                'success': False,
                'message': 'Failed to create booking. Please try again.'
            }), 500
        
        # Send confirmation email to client
        email_sent, email_message = email_service.send_booking_confirmation(
            data, 
            result['booking_reference']
        )
        
        # Send admin notification (don't fail the request if this fails)
        admin_notified, _ = email_service.send_admin_notification(
            data, 
            result['booking_reference']
        )
        
        # Prepare response
        response_data = {
            'success': True,
            'message': 'Your booking has been received! A confirmation email has been sent to your email address.',
            'booking_id': result['booking_id'],
            'booking_reference': result['booking_reference'],
            'email_sent': email_sent,
            'total_price': total_price
        }
        
        return jsonify(response_data), 201
        
    except Exception as e:
        app.logger.error(f"Booking error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An unexpected error occurred. Please try again later.'
        }), 500

@app.route('/api/booking/<reference>', methods=['GET'])
def get_booking(reference):
    """
    Get booking details by reference (for client to check status)
    """
    try:
        # Search for booking by reference
        # Note: You need to implement this method in models.py
        # For now, return not found
        return jsonify({
            'success': False,
            'message': 'Booking not found'
        }), 404
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Error retrieving booking'
        }), 500

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'success': False,
        'message': 'Endpoint not found'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({
        'success': False,
        'message': 'Internal server error'
    }), 500

# Admin endpoints (protected)
#@app.route('/api/admin/bookings', methods=['GET'])
#@rate_limit(limit_per_hour=200)
#def get_all_bookings():
    """
    Get all bookings (admin only - would need authentication)
    For now, this is a simple endpoint. In production, add admin authentication.
    """
    try:
        # Check for admin auth (simplified - add proper auth in production)
        admin_key = request.headers.get('X-Admin-Key')
        if admin_key != Config.JWT_SECRET_KEY:
            return jsonify({
                'success': False,
                'message': 'Unauthorized access'
            }), 401
        
        limit = request.args.get('limit', 100, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        bookings = db.get_all_bookings(limit, offset)
        
        return jsonify({
            'success': True,
            'data': bookings,
            'count': len(bookings)
        }), 200
        
    except Exception as e:
        app.logger.error(f"Admin error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Error retrieving bookings'
        }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=app.config['DEBUG'])
