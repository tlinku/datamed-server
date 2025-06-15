from functools import wraps
from flask import request, jsonify, current_app
import jwt
import requests
from keycloak import KeycloakOpenID, KeycloakAdmin
from datetime import datetime, timedelta, timezone

def get_keycloak_client():
    server_url = current_app.config.get('KEYCLOAK_URL', 'http://keycloak:8080') + '/auth'
    client_id = current_app.config.get('KEYCLOAK_CLIENT_ID', 'datamed-client')
    realm_name = current_app.config.get('KEYCLOAK_REALM', 'datamed')
    client_secret = current_app.config.get('KEYCLOAK_CLIENT_SECRET', None)

    return KeycloakOpenID(
        server_url=server_url,
        client_id=client_id,
        realm_name=realm_name,
        client_secret_key=client_secret
    )
def get_keycloak_public_key():
    server_url = current_app.config.get('KEYCLOAK_URL', 'http://keycloak:8080') + '/auth'
    realm_name = current_app.config.get('KEYCLOAK_REALM', 'datamed')

    url = f"{server_url}/realms/{realm_name}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        public_key = data.get('public_key')
        if public_key:
            return f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"
        return None
    except Exception as e:
        return None
def keycloak_token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return jsonify({'error': 'Authorization header is missing'}), 401

        try:
            parts = auth_header.split()
            if len(parts) != 2 or parts[0].lower() != 'bearer':
                return jsonify({'error': 'Invalid authorization header format'}), 401
            token = parts[1]
            public_key = get_keycloak_public_key()
            if not public_key:
                return jsonify({'error': 'Could not retrieve Keycloak public key'}), 500
            options = {
                'verify_signature': True,
                'verify_aud': False,
                'verify_exp': True
            }
            try:
                decoded_token = jwt.decode(
                    token,
                    public_key,
                    algorithms=['RS256'],
                    options=options
                )
            except Exception as decode_error:
                return jsonify({'error': f'Token decode error: {decode_error}'}), 401
            user_id = decoded_token.get('sub')
            if not user_id:
                return jsonify({'error': 'Invalid token: missing subject'}), 401
            exp = decoded_token.get('exp')
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                return jsonify({'error': 'Token has expired'}), 401
            realm_access = decoded_token.get('realm_access', {})
            roles = realm_access.get('roles', [])
            return f(user_id, roles, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError as e:
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            return jsonify({'error': 'Token validation failed'}), 401

    return decorator
def get_user_info(token):
    try:
        keycloak_client = get_keycloak_client()
        user_info = keycloak_client.userinfo(token)
        return user_info
    except Exception as e:
        return None
def get_keycloak_admin():
    server_url = current_app.config.get('KEYCLOAK_URL', 'http://keycloak:8080') + '/auth'
    realm_name = current_app.config.get('KEYCLOAK_REALM', 'datamed')
    admin_username = 'admin'
    admin_password = 'admin'

    try:
        keycloak_admin = KeycloakAdmin(
            server_url=server_url,
            username=admin_username,
            password=admin_password,
            realm_name=realm_name,
            verify=True
        )
        return keycloak_admin
    except Exception as e:
        return None
def create_keycloak_user(email, password, first_name=None, last_name=None):
    try:
        keycloak_admin = get_keycloak_admin()
        if not keycloak_admin:
            raise Exception("Could not initialize Keycloak admin client")
        user_data = {
            "email": email,
            "username": email,
            "enabled": True,
            "emailVerified": True,
            "credentials": [
                {
                    "type": "password",
                    "value": password,
                    "temporary": False
                }
            ]
        }
        if first_name:
            user_data["firstName"] = first_name
        if last_name:
            user_data["lastName"] = last_name
        user_id = keycloak_admin.create_user(user_data)
        return user_id
    except Exception as e:
        raise
def delete_keycloak_user(user_id):
    try:
        keycloak_admin = get_keycloak_admin()
        if not keycloak_admin:
            raise Exception("Could not initialize Keycloak admin client")
        keycloak_admin.delete_user(user_id)
        return True
    except Exception as e:
        return False
def find_keycloak_user_by_email(email):
    try:
        keycloak_admin = get_keycloak_admin()
        if not keycloak_admin:
            raise Exception("Could not initialize Keycloak admin client")
        users = keycloak_admin.get_users({"email": email})

        if not users or len(users) == 0:
            return None
        user = users[0]
        return user['id']
    except Exception as e:
        return None
