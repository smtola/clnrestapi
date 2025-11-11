from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager
from flask_swagger_ui import get_swaggerui_blueprint

mongo = PyMongo()
jwt = JWTManager()

def init_app(app):
    # Swagger UI blueprint
    swagger_url = '/api/v1/docs'
    api_url = '/static/swagger/swagger.yaml'  
    swaggerui_blueprint = get_swaggerui_blueprint(
        swagger_url,
        api_url,
        config={'app_name':'CLN REST API'}
    )
    app.register_blueprint(swaggerui_blueprint, url_prefix=swagger_url)
    return app

swagger = type('Swagger', (), {'init_app': init_app})