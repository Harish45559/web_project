import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'postgresql://postgresql_localhost_qwerty123atyour_5frn_user:KqIITzJLZkiIOOYTE4s7dOLgQQn0h37J@dpg-cu96c6d6l47c73d6j9k0-a/postgresql_localhost_qwerty123atyour_5frn')
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///default.db')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
