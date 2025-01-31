from flask import Flask
from psycopg2.pool import SimpleConnectionPool
import os
from dotenv import load_dotenv
from .routes.auth import auth_bp
from .routes.prescriptions_api import prescriptions_bp
from .routes.special_searches import prescription_routes
from .routes.doctors_api import doctors_bp
from .routes.notes_api import notes_bp
load_dotenv()

def create_app():
    app = Flask(__name__)
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
    
    return app