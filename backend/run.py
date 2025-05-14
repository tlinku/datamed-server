from app import create_app
import os
import pathlib

app, socketio = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    # Check if SSL certificate files exist
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

    socketio.run(app, **kwargs)
