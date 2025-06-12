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
    print(f"Attempting to connect to: {url}")
    try:
        response = requests.get(url)
        print(f"Response status: {response.status_code}")
        response.raise_for_status()
        data = response.json()
        print(f"Response keys: {list(data.keys())}")
        public_key = data.get('public_key')
        if public_key:
            print("Successfully retrieved Keycloak public key")
            return f"-----BEGIN PUBLIC KEY-----\n{public_key}\n-----END PUBLIC KEY-----"
        else:
            print("No public_key found in response")
        return None
    except Exception as e:
        print(f"Error getting Keycloak public key: {str(e)}")
        return None
def keycloak_token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        print("=== Keycloak Token Decorator called ===")
        print("Headers:", request.headers)

        token = None
        auth_header = request.headers.get('Authorization')
        print(f"Auth header: {auth_header}")

        if not auth_header:
            print("No Authorization header found!")
            return jsonify({'error': 'Authorization header is missing'}), 401

        try:
            parts = auth_header.split()
            print(f"Header parts: {parts}")

            if len(parts) != 2 or parts[0].lower() != 'bearer':
                print("Invalid authorization header format!")
                return jsonify({'error': 'Invalid authorization header format'}), 401

            token = parts[1]
            print(f"Token to decode (first 80 chars): {token[:80]}{'...' if len(token) > 80 else ''}")
            print("Connecting to Keycloak to get public key...")
            public_key = get_keycloak_public_key()
            print(f"Public key received: {public_key[:40]}..." if public_key else "No public key received!")
            if not public_key:
                return jsonify({'error': 'Could not retrieve Keycloak public key'}), 500
            options = {
                'verify_signature': True,
                'verify_aud': False,
                'verify_exp': True
            }

            print("Decoding token...")
            try:
                decoded_token = jwt.decode(
                    token,
                    public_key,
                    algorithms=['RS256'],
                    options=options
                )
            except Exception as decode_error:
                print(f"Token decode error: {decode_error}")
                return jsonify({'error': f'Token decode error: {decode_error}'}), 401

            print(f"Decoded token: {decoded_token}")

            user_id = decoded_token.get('sub')
            if not user_id:
                print("Token missing subject (sub)!")
                return jsonify({'error': 'Invalid token: missing subject'}), 401
            exp = decoded_token.get('exp')
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                print("Token has expired!")
                return jsonify({'error': 'Token has expired'}), 401
            realm_access = decoded_token.get('realm_access', {})
            roles = realm_access.get('roles', [])

            print(f"User ID: {user_id}, Roles: {roles}")
            return f(user_id, roles, *args, **kwargs)

        except jwt.ExpiredSignatureError:
            print("Token expired (jwt.ExpiredSignatureError)")
            return jsonify({'error': 'Token has expired'}), 401
        except jwt.InvalidTokenError as e:
            print(f"Invalid token (jwt.InvalidTokenError): {str(e)}")
            return jsonify({'error': 'Invalid token'}), 401
        except Exception as e:
            print(f"Other error during token validation: {str(e)}")
            return jsonify({'error': 'Token validation failed'}), 401

    return decorator
def get_user_info(token):
    try:
        keycloak_client = get_keycloak_client()
        user_info = keycloak_client.userinfo(token)
        return user_info
    except Exception as e:
        print(f"Error getting user info: {str(e)}")
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
        print(f"Error creating Keycloak admin client: {str(e)}")
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

        print(f"Created Keycloak user with ID: {user_id}")
        return user_id
    except Exception as e:
        print(f"Error creating Keycloak user: {str(e)}")
        raise
def delete_keycloak_user(user_id):
    try:
        keycloak_admin = get_keycloak_admin()
        if not keycloak_admin:
            raise Exception("Could not initialize Keycloak admin client")
        keycloak_admin.delete_user(user_id)

        print(f"Deleted Keycloak user with ID: {user_id}")
        return True
    except Exception as e:
        print(f"Error deleting Keycloak user: {str(e)}")
        return False
def find_keycloak_user_by_email(email):
    try:
        keycloak_admin = get_keycloak_admin()
        if not keycloak_admin:
            raise Exception("Could not initialize Keycloak admin client")
        users = keycloak_admin.get_users({"email": email})

        if not users or len(users) == 0:
            print(f"No Keycloak user found with email: {email}")
            return None
        user = users[0]
        print(f"Found Keycloak user with ID: {user['id']} for email: {email}")
        return user['id']
    except Exception as e:
        print(f"Error finding Keycloak user by email: {str(e)}")
        return None
