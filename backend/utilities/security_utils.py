import re
from flask import request, jsonify
from functools import wraps
import os

class InputValidator:
    @staticmethod
    def validate_pesel(pesel):
        """Validate Polish PESEL number with checksum"""
        if not pesel or len(pesel) != 11 or not pesel.isdigit():
            return False
        weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
        checksum = sum(int(pesel[i]) * weights[i] for i in range(10)) % 10
        checksum = (10 - checksum) % 10
        
        return int(pesel[10]) == checksum
    
    @staticmethod
    def validate_email(email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_name(name):
        if not name or len(name) < 2 or len(name) > 50:
            return False
        pattern = r'^[a-zA-ZąćęłńóśźżĄĆĘŁŃÓŚŹŻ\s\-\']+$'
        return re.match(pattern, name) is not None
    
    @staticmethod
    def validate_password(password):
        if not password or len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter"
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter"
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit"
        
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return False, "Password must contain at least one special character"
        
        return True, "Password is valid"
    
    @staticmethod
    def sanitize_string(input_string):
        """Basic string sanitization"""
        if not input_string:
            return ""
        return re.sub(r'[<>"\';\\]', '', str(input_string).strip())

def validate_file_upload(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'pdf_file' in request.files:
            file = request.files['pdf_file']
            max_size = int(os.getenv('MAX_FILE_SIZE', 10485760))  
            if file and len(file.read()) > max_size:
                return jsonify({'error': 'File too large. Maximum size is 10MB'}), 400
            file.seek(0)  
            allowed_extensions = os.getenv('ALLOWED_EXTENSIONS', 'pdf').split(',')
            if file.filename:
                ext = file.filename.rsplit('.', 1)[1].lower()
                if ext not in allowed_extensions:
                    return jsonify({'error': f'Invalid file type. Allowed: {", ".join(allowed_extensions)}'}), 400
            if file.filename and file.filename.endswith('.pdf'):
                file_header = file.read(4)
                file.seek(0)  
                if file_header != b'%PDF':
                    return jsonify({'error': 'Invalid PDF file'}), 400
        
        return f(*args, **kwargs)
    return decorated_function

def rate_limit_decorator(max_requests=60, per_seconds=60):
    from collections import defaultdict
    import time
    
    requests_dict = defaultdict(list)
    
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            client_ip = request.environ.get('HTTP_X_FORWARDED_FOR', request.remote_addr)
            current_time = time.time()
            requests_dict[client_ip] = [
                req_time for req_time in requests_dict[client_ip]
                if current_time - req_time < per_seconds
            ]
            if len(requests_dict[client_ip]) >= max_requests:
                return jsonify({'error': 'Rate limit exceeded'}), 429
            requests_dict[client_ip].append(current_time)
            return f(*args, **kwargs)
        return decorated_function
    return decorator
