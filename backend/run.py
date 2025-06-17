from app import create_app
import os
import pathlib
import requests
from flask import current_app

app, socketio = create_app()
def check_keycloak_connectivity():
    keycloak_url = app.config.get('KEYCLOAK_URL', 'http://keycloak:8080')
    realm = app.config.get('KEYCLOAK_REALM', 'datamed')
    url = f"{keycloak_url}/auth/realms/{realm}"  
    try:
        resp = requests.get(url, timeout=5)
    except Exception as e:
        print(f"ERROR: Could not connect to Keycloak at {url}: {e}")

check_keycloak_connectivity()

if __name__ == '__main__':
    print("Debug: Starting main application...")
    port = int(os.getenv('PORT', 5000))
    key_file = "./klucz_bez_hasla.key"
    cert_file = "./certyfikat.crt"
    use_ssl = pathlib.Path(key_file).exists() and pathlib.Path(cert_file).exists()
    
    print(f"Debug: Port: {port}, SSL: {use_ssl}")

    kwargs = {
        'host': '0.0.0.0',
        'port': port,
        'debug': os.getenv('FLASK_ENV') == 'development',
        'use_reloader': False  # Disable reloader in Kubernetes
    }

    if use_ssl:
        kwargs['keyfile'] = key_file
        kwargs['certfile'] = cert_file

    print(f"Debug: Starting SocketIO server with kwargs: {kwargs}")
    socketio.run(app, allow_unsafe_werkzeug=True, **kwargs)
