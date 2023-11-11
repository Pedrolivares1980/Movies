# For a production app, you should use a secret key set in the environment
# The recommended way to generate a 64char secret key is to run:
# python -c 'import secrets; print(secrets.token_hex())'
import os

class Config:
    """
    Base configuration class. Contains default configuration settings.
    """
    SECRET_KEY = 'your_very_secure_secret_key'  # WARNING: Keep this secret and use a secure method to manage it for production
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db.sqlite3'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'images', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB upload limit
    MAX_IMAGE_FILESIZE = 0.5 * 1024 * 1024  # 0.5 MB


class DevelopmentConfig(Config):
    """
    Development configuration class. Overrides default configuration with development-specific settings.
    """
    DEBUG = True
    SQLALCHEMY_ECHO = True  # Helps in debugging by printing SQL queries


class TestingConfig(Config):
    """
    Testing configuration class. Overrides default configuration with testing-specific settings.
    """
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'  # Use in-memory SQLite database for tests


class ProductionConfig(Config):
    """
    Production configuration class. Overrides default configuration with production-specific settings.
    """
    DEBUG = False
    SQLALCHEMY_ECHO = False


