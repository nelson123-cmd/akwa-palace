from functools import wraps
from flask import request, jsonify, g
import time
from datetime import datetime, timedelta
from collections import defaultdict
import hashlib
import hmac
from config import Config

# Rate limiting storage (use Redis in production)
rate_limit_storage = defaultdict(list)

def rate_limit(limit_per_hour=100):
    """Rate limiting decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.remote_addr
            
            # Clean old requests (older than 1 hour)
            current_time = time.time()
            rate_limit_storage[client_ip] = [
                req_time for req_time in rate_limit_storage[client_ip] 
                if current_time - req_time < 3600
            ]
            
            # Check rate limit
            if len(rate_limit_storage[client_ip]) >= limit_per_hour:
                return jsonify({
                    'success': False,
                    'message': 'Rate limit exceeded. Please try again later.'
                }), 429
            
            # Add current request
            rate_limit_storage[client_ip].append(current_time)
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def validate_json(required_fields=None):
    """Validate JSON payload decorator"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not request.is_json:
                return jsonify({
                    'success': False,
                    'message': 'Content-Type must be application/json'
                }), 400
            
            data = request.get_json()
            
            if required_fields:
                missing_fields = [field for field in required_fields if field not in data]
                if missing_fields:
                    return jsonify({
                        'success': False,
                        'message': f'Missing required fields: {", ".join(missing_fields)}'
                    }), 400
            
            g.request_data = data
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def security_headers(response):
    """Add security headers to all responses"""
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

def sanitize_data(keys_to_sanitize=None):
    """Sanitize specific fields in request data"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if hasattr(g, 'request_data') and g.request_data:
                if keys_to_sanitize:
                    for key in keys_to_sanitize:
                        if key in g.request_data and g.request_data[key]:
                            from utils import validator
                            g.request_data[key] = validator.sanitize_input(g.request_data[key])
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def require_api_key(f):
    """Require API key for admin endpoints"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        expected_key = Config.JWT_SECRET_KEY
        
        if not api_key or not hmac.compare_digest(api_key, expected_key):
            return jsonify({
                'success': False,
                'message': 'Invalid or missing API key'
            }), 401
        
        return f(*args, **kwargs)
    return decorated_function
