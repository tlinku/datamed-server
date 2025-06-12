from app import create_app
import os
import pathlib
import requests
from flask import current_app

app, socketio = create_app()

# --- Keycloak connectivity check ---
def check_keycloak_connectivity():
    keycloak_url = app.config.get('KEYCLOAK_URL', 'http://keycloak:8080')
    realm = app.config.get('KEYCLOAK_REALM', 'datamed')
    url = f"{keycloak_url}/auth/realms/{realm}"  # Keycloak realm endpoint
    try:
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200 and 'public_key' in resp.json():
            print(f"Keycloak connectivity check: OK (realm '{realm}' found, public key present)")
        else:
            print(f"WARNING: Keycloak connectivity check: Unexpected response from {url} (status {resp.status_code})")
    except Exception as e:
        print(f"ERROR: Could not connect to Keycloak at {url}: {e}")

check_keycloak_connectivity()
# --- End Keycloak connectivity check ---

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    key_file = "./klucz_bez_hasla.key"
    cert_file = "./certyfikat.crt"
    use_ssl = pathlib.Path(key_file).exists() and pathlib.Path(cert_file).exists()

    kwargs = {
        'host': '0.0.0.0',
        'port': port,
        'debug': os.getenv('FLASK_ENV') == 'development',
        'use_reloader': True
    }

    if use_ssl:
        kwargs['keyfile'] = key_file
        kwargs['certfile'] = cert_file
        print("Using SSL with provided certificate files")
    else:
        print("SSL certificate files not found, running without SSL")

    socketio.run(app, allow_unsafe_werkzeug=True, **kwargs)
