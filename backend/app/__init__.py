from flask import Flask
from psycopg2.pool import SimpleConnectionPool
import os

def create_app():
    app = Flask(__name__)
    
    DATABASE_URL = os.getenv('DATABASE_URL')
    if not DATABASE_URL:
        raise ValueError("No DATABASE_URL set in environment")
    
    # Create connection pool
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
    
    # Register blueprints
    from .routes.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    return app