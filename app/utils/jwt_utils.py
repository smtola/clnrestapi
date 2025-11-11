from flask_jwt_extended import create_access_token as flask_create_access_token

def create_access_token(identity, additional_claims=None):
    return flask_create_access_token(identity=identity, additional_claims=additional_claims or {})