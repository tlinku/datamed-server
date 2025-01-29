from functools import wraps
from flask import request, jsonify, current_app
import jwt
from datetime import datetime, timedelta, timezone

def create_token(user_id: int):
    payload = {
        'user_id': user_id,
        'exp': datetime.now(timezone.utc) + timedelta(days=1)
    }
    return jwt.encode(payload, current_app.config['TOKEN_KEY'], algorithm='HS256')


def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        print("=== Decorator called ===")  # Debug entry point
        print("Headers:", request.headers)  # Show all headers
        
        token = None
        auth_header = request.headers.get('Authorization')
        print(f"Auth header: {auth_header}")  # Show auth header
        
        if not auth_header:
            return jsonify({'error': 'Authorization header is missing'}), 401
            
        try:
            parts = auth_header.split()
            print(f"Header parts: {parts}")  # Show split result
            
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return jsonify({'error': 'Invalid authorization header format'}), 401
                
            token = parts[1]
            print(f"Token to decode: {token}")  # Show token before decode
            
            data = jwt.decode(token, current_app.config['TOKEN_KEY'], algorithms=['HS256'])  # Note: TOKEN_KEY not SECRET_KEY
            print(f"Decoded data: {data}")  # Show decoded data
            
            current_user_id = data['user_id']
            print(f"User ID: {current_user_id}")  # Show extracted user_id
            
            return f(current_user_id, *args, **kwargs)
        except jwt.ExpiredSignatureError:
            print("Token expired")  # Debug expired
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError as e:
            print(f"Invalid token: {str(e)}")  # Debug invalid
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            print(f"Other error: {str(e)}")  # Debug other errors
            return jsonify({'error': 'Token validation failed'}), 401
            
    return decorator