from flask import request, current_app
from time import time
import logging
from logging.handlers import RotatingFileHandler
import os

class RequestLoggingMiddleware:
    def __init__(self, wsgi_app):
        self.wsgi_app = wsgi_app
        
        if not os.path.exists('logs'):
            os.makedirs('logs')
            
        handler = RotatingFileHandler(
            'logs/app.log',
            maxBytes=10485760,
            backupCount=5
        )
        
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        self.logger = logging.getLogger('app')
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def __call__(self, environ, start_response):
        path = environ.get('PATH_INFO')
        method = environ.get('REQUEST_METHOD')
        start_time = time()
        
        def logging_start_response(status, headers, *args):
            duration = time() - start_time
            status_code = int(status.split()[0])
            self.logger.info(
                f'{method} {path} {status_code} - {duration:.2f}s'
            )
            return start_response(status, headers, *args)
            
        return self.wsgi_app(environ, logging_start_response)