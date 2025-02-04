from app import create_app
import os

app, socketio = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    socketio.run(
        app,
        host='0.0.0.0',
        port=port,
        debug=os.getenv('FLASK_ENV') == 'development',
        use_reloader=True,
        keyfile="./klucz_bez_hasla.key",
        certfile="./certyfikat.crt"
    )