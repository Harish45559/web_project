import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('postgresql://postgresql_postgres_qwerty123at5432_user:8NgAmKjVFXhs8Es8OIjySXSQlZo09kk7@dpg-cu97n0lds78s73bfhtgg-a/postgresql_postgres_qwerty123at5432')  # Make sure this line is correct
    SQLALCHEMY_TRACK_MODIFICATIONS = False
