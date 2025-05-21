from flask import Flask
from flask_socketio import SocketIO
from psycopg2.pool import SimpleConnectionPool
from flask_cors import CORS 
from dotenv import load_dotenv
from logger import RequestLoggingMiddleware
from utilities.minio_handler import MinioHandler
import os

from .routes.auth import auth_bp
from .routes.prescriptions_api import prescriptions_bp
from .routes.special_searches import prescription_routes
from .routes.doctors_api import doctors_bp
from .routes.notes_api import notes_bp

load_dotenv()

def create_app():
    app = Flask(__name__)
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

    app.config['TOKEN_KEY'] = os.getenv('TOKEN_KEY')
    if not app.config['TOKEN_KEY']:
        raise ValueError("No TOKEN_KEY set in environment")

    # Keycloak configuration
    app.config['KEYCLOAK_URL'] = os.getenv('KEYCLOAK_URL', 'http://keycloak:8080')
    app.config['KEYCLOAK_REALM'] = os.getenv('KEYCLOAK_REALM', 'datamed')
    app.config['KEYCLOAK_CLIENT_ID'] = os.getenv('KEYCLOAK_CLIENT_ID', 'datamed-client')
    app.config['KEYCLOAK_CLIENT_SECRET'] = os.getenv('KEYCLOAK_CLIENT_SECRET')

    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("No DATABASE_URL set in environment")

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
    app.register_blueprint(prescription_routes)
    app.register_blueprint(doctors_bp)
    app.register_blueprint(notes_bp)


    try:
        minio_handler = MinioHandler()
        minio_handler.init_app(app)
        app.minio_handler = minio_handler
        print("MinIO connection established")
    except Exception as e:
        print(f"Error connecting to MinIO: {e}")

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
