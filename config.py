import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY','postgresql://localhost:qwerty123@your_host:5432/project' )
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://localhost:qwerty123@your_host:5432/project')
    SQLALCHEMY_DATABASE_URI = DATABASE_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
