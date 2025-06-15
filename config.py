import os

class Config:
    # Secret key for CSRF protection in forms
    SECRET_KEY = os.environ.get('SECRET_KEY', 'your_default_secret_key')

    # SQLAlchemy database URI (update with your DB info)
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL', 'sqlite:///finance_tracker.db')

    # Track modifications - turn off for performance
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # WTForms settings
    WTF_CSRF_ENABLED = True

    # Other configs (optional)
    DEBUG = True
