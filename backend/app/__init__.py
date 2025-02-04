from flask import Flask
from flask_socketio import SocketIO
from psycopg2.pool import SimpleConnectionPool
from flask_cors import CORS 
from dotenv import load_dotenv
from logger import RequestLoggingMiddleware
from utilities.mqtt_handler import MQTTHandler
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
    socketio = SocketIO(app, cors_allowed_origins="*")
    mqtt_handler = MQTTHandler(socketio)
    os.system("utilities/mqtt.sh start")
    if mqtt_handler.connect():
            print("MQTT broker connection established")
    else:
        print("MQTT broker connection failed")
    
    app.wsgi_app = RequestLoggingMiddleware(app.wsgi_app)
    
    app.config['TOKEN_KEY'] = os.getenv('TOKEN_KEY')
    if not app.config['TOKEN_KEY']:
        raise ValueError("No TOKEN_KEY set in environment")
    
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
        mqtt_handler.connect()
        app.mqtt_handler = mqtt_handler
        print("MQTT connection established")
    except Exception as e:
        print(f"Error connecting to MQTT broker: {e}")
    
    @app.errorhandler(404)
    def not_found_error(error):
        return {'error': 'Not Found'}, 404

    @app.errorhandler(500)
    def internal_error(error):
        return {'error': 'Internal Server Error'}, 500
    
    return app, socketio