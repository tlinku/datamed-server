from werkzeug.security import generate_password_hash

class Authentication:
    @staticmethod
    def create_account(email, password):
        password_hash = generate_password_hash(password)
        return {"email": email, "password_hash": password_hash}
    def hash_password(password):
        return generate_password_hash(password)