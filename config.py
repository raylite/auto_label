import os, binascii
from dotenv import load_dotenv

APP_ROOT = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(APP_ROOT, '.env'))

class Config(object):
    DeBUG = False
    TESTING = False
    SECRET_KEY = binascii.hexlify(os.urandom(24))
    SQLALCHEMY_DATABASE_URI = f"{os.getenv('DATABASE_URL')}{os.getenv('DB_ADMIN')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_MAX_OVERFLOW = int(os.getenv('MAX_OVERFLOW'))
    MYSQL_DATABASE_CHARSET = 'utf8mb4'
    DATA_FOLDER = os.path.join(APP_ROOT, 'data')
    
class ProductionConfig(Config):
    pass

class DevelopmentConfig(Config):
    DEBUG = True
    
class TestingConfig(Config):
    Testing = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'