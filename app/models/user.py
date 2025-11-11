from werkzeug.security import generate_password_hash, check_password_hash

class User:
    def __init__(self, username, email, password, role, is_verified=False):
        self.username = username
        self.email = email
        self.password_hash = generate_password_hash(password)
        self.role = role
        self.is_verified = is_verified

    @staticmethod
    def check_password(hash, password):
        return check_password_hash(hash, password)
    