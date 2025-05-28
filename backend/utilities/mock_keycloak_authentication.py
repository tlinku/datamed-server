"""
Mock Keycloak authentication for testing
This module provides mock authentication that simulates Keycloak behavior
"""

import json
import base64
from functools import wraps
from flask import request, jsonify, g
import logging

logger = logging.getLogger(__name__)

class MockKeycloakAuth:
    """Mock Keycloak authentication class"""
    
    def __init__(self):
        self.mock_users = {
            'test-doctor': {
                'id': 'test-user-id-123',
                'username': 'test-doctor',
                'first_name': 'Test',
                'last_name': 'Doctor',
                'email': 'test.doctor@datamed.com',
                'roles': ['doctor', 'user']
            }
        }
    
    def validate_token(self, token):
        """Validate a mock JWT token"""
        try:
            # Split the token
            if not token or token.count('.') != 2:
                return None
                
            header, payload, signature = token.split('.')
            
            # Decode payload (in real JWT this would also verify signature)
            decoded_payload = base64.b64decode(payload + '==')  # Add padding if needed
            payload_data = json.loads(decoded_payload)
            
            # Check if token is expired
            import time
            current_time = int(time.time())
            if current_time >= payload_data.get('exp', 0):
                logger.warning("Mock token is expired")
                return None
            
            # Return user info
            username = payload_data.get('preferred_username')
            if username in self.mock_users:
                user_info = self.mock_users[username].copy()
                user_info['token_data'] = payload_data
                return user_info
            
            return None
            
        except Exception as e:
            logger.error(f"Error validating mock token: {e}")
            return None
    
    def get_user_id(self, token):
        """Get user ID from token"""
        user_info = self.validate_token(token)
        return user_info['id'] if user_info else None
    
    def get_user_roles(self, token):
        """Get user roles from token"""
        user_info = self.validate_token(token)
        return user_info['roles'] if user_info else []
    
    def has_role(self, token, role):
        """Check if user has specific role"""
        roles = self.get_user_roles(token)
        return role in roles

# Global mock auth instance
mock_auth = MockKeycloakAuth()

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            logger.warning("No valid Authorization header found")
            return jsonify({'error': 'Authentication required'}), 401
        
        token = auth_header.split(' ')[1]
        user_info = mock_auth.validate_token(token)
        
        if not user_info:
            logger.warning("Invalid or expired token")
            return jsonify({'error': 'Invalid or expired token'}), 401
        
        # Store user info in Flask's g object for use in route handlers
        g.current_user = user_info
        g.user_id = user_info['id']
        g.username = user_info['username']
        
        logger.info(f"Mock authentication successful for user: {user_info['username']}")
        return f(*args, **kwargs)
    
    return decorated_function

def require_role(role):
    """Decorator to require specific role"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # This should be used after require_auth
            if not hasattr(g, 'current_user'):
                return jsonify({'error': 'Authentication required'}), 401
            
            if role not in g.current_user['roles']:
                logger.warning(f"User {g.username} does not have required role: {role}")
                return jsonify({'error': f'Role {role} required'}), 403
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

def get_current_user():
    """Get current authenticated user"""
    return getattr(g, 'current_user', None)

def get_user_id():
    """Get current user ID"""
    return getattr(g, 'user_id', None)

def get_username():
    """Get current username"""
    return getattr(g, 'username', None)
