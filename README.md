<!-- Structure -->
project_root/
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py
│   ├── routes/
│   │   ├── __init__.py
│   │   └── auth.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user_schema.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── jwt_utils.py
│   │   └── email_otp.py
│   └── extensions.py
│
├── requirements.txt
├── run.py
└── static/
    └── swagger/
        └── swagger.yaml

Explanation
app/: Main application package.

config.py: Configuration (MongoDB URI, JWT secret, etc.).
models/: Data models (e.g., User).
routes/: Flask routes/Blueprints (e.g., auth endpoints).
schemas/: Marshmallow schemas for request/response validation.
utils/: Utility functions (JWT, OTP, etc.).
extensions.py: Extensions initialization (PyMongo, JWT, etc.).
requirements.txt: Python dependencies.

run.py: Application entrypoint.

swagger/: Swagger YAML for API documentation.