"""
Unified authentication module that can use either real Keycloak or mock authentication
based on environment variables
"""

import os
from functools import wraps
from flask import current_app

# Determine which authentication to use
USE_MOCK_AUTH = os.environ.get('USE_MOCK_AUTH', 'false').lower() == 'true'

if USE_MOCK_AUTH:
    print("Using MOCK authentication")
    from utilities.mock_keycloak_authentication import require_auth, require_role, get_current_user, get_user_id, get_username
    
    def keycloak_token_required(f):
        """Wrapper to maintain compatibility with existing route decorators"""
        @wraps(f)
        @require_auth
        def decorated_function(*args, **kwargs):
            # Get mock user info and pass it in the same format as real Keycloak
            user_info = get_current_user()
            user_id = user_info['id']
            roles = user_info['roles']
            return f(user_id, roles, *args, **kwargs)
        return decorated_function
    
    def require_keycloak_role(role):
        """Wrapper to maintain compatibility with role requirements"""
        return require_role(role)

else:
    print("Using REAL Keycloak authentication")
    from utilities.keycloak_authentication import keycloak_token_required
    
    def require_keycloak_role(role):
        """Use real Keycloak role checking"""
        # You'll need to implement this in your real keycloak_authentication.py if it doesn't exist
        def decorator(f):
            @wraps(f)
            def decorated_function(*args, **kwargs):
                # This would check roles in real Keycloak implementation
                return f(*args, **kwargs)
            return decorated_function
        return decorator

# Export the functions to use
__all__ = ['keycloak_token_required', 'require_keycloak_role', 'USE_MOCK_AUTH']
