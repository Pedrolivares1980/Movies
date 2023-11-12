# For a production app, you should use a secret key set in the environment
# The recommended way to generate a 64char secret key is to run:
# python -c 'import secrets; print(secrets.token_hex())'
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'not-set')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///db.sqlite3' ) 
    SQLALCHEMY_ECHO = True
    UPLOAD_FOLDER = os.path.join(os.getcwd(), 'static', 'images', 'uploads')
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16 MB upload limit
    MAX_IMAGE_FILESIZE = 0.5 * 1024 * 1024  # 0.5 MB
