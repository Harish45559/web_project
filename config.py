import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///default.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
