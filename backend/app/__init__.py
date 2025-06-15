from flask import Flask, request, g
from flask_socketio import SocketIO
from psycopg2.pool import SimpleConnectionPool
from flask_cors import CORS 
from dotenv import load_dotenv
from logger import RequestLoggingMiddleware
from utilities.minio_handler import MinioHandler
import os
import secrets

def read_secret(secret_path, fallback_env=None):
    try:
        if os.path.exists(secret_path):
            with open(secret_path, 'r') as f:
                return f.read().strip()
    except Exception as e:
        print(f"Warning: Could not read secret from {secret_path}: {e}")
    
    if fallback_env:
        return os.getenv(fallback_env)
    
    return None

from .routes.auth import auth_bp
from .routes.prescriptions_api import prescriptions_bp
from .routes.doctors_api import doctors_bp
from .routes.notes_api import notes_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
    app.config['SESSION_COOKIE_SECURE'] = True
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
    app.config['PERMANENT_SESSION_LIFETIME'] = 3600
    @app.after_request
    def add_security_headers(response):
        response.headers['X-Content-Type-Options'] = 'nosniff'
        response.headers['X-Frame-Options'] = 'DENY'
        response.headers['X-XSS-Protection'] = '1; mode=block'
        response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'"
        response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        return response
    
    CORS(app,
         supports_credentials=True,
         resources={r"/*": {
             "origins": ["http://localhost:3000","http://0.0.0.0:5000"],
             "allow_headers": ["Content-Type", "Authorization"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "expose_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "send_wildcard": False,
             "intercept_exceptions": True
         }})
    socketio = SocketIO(app, cors_allowed_origins=["http://localhost:3000", "http://0.0.0.0:5000"])

    app.wsgi_app = RequestLoggingMiddleware(app.wsgi_app)
    token_key = read_secret('/run/secrets/token_key', 'TOKEN_KEY')
    postgres_password = read_secret('/run/secrets/postgres_password', 'POSTGRES_PASSWORD')
    
    app.config['TOKEN_KEY'] = token_key
    if not app.config['TOKEN_KEY']:
        raise ValueError("No TOKEN_KEY set in environment or secrets")
    app.config['KEYCLOAK_URL'] = os.getenv('KEYCLOAK_URL', 'http://keycloak:8080')
    app.config['KEYCLOAK_REALM'] = os.getenv('KEYCLOAK_REALM', 'datamed')
    app.config['KEYCLOAK_CLIENT_ID'] = os.getenv('KEYCLOAK_CLIENT_ID', 'datamed-client')
    app.config['KEYCLOAK_CLIENT_SECRET'] = os.getenv('KEYCLOAK_CLIENT_SECRET')
    postgres_user = os.getenv('POSTGRES_USER', 'datamed')
    postgres_db = os.getenv('POSTGRES_DB', 'datamed')
    DATABASE_URL = f"postgresql://{postgres_user}:{postgres_password}@postgres:5432/{postgres_db}"
    
    if not postgres_password:
        raise ValueError("No POSTGRES_PASSWORD set in environment or secrets")

    try:
        app.db_pool = SimpleConnectionPool(
            minconn=1,
            maxconn=10,
            dsn=DATABASE_URL
        )
        print("Database pool created successfully")
    except Exception as e:
        print(f"Error creating database pool: {e}")
        raise

    app.register_blueprint(auth_bp)
    app.register_blueprint(prescriptions_bp)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(notes_bp)
    minio_handler = None
    try:
        minio_handler = MinioHandler()
        minio_handler.init_app(app)
        app.config['MINIO_AVAILABLE'] = True
        print("MinIO connection established")
    except Exception as e:
        print(f"Error connecting to MinIO: {e}")
        app.config['MINIO_AVAILABLE'] = False
        minio_handler = None
    app.minio_handler = minio_handler

    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not Found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal Server Error'}, 500

    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'healthy'}, 200

    return app, socketio
