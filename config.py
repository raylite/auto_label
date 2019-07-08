import os, binascii
from dotenv import load_dotenv

APP_ROOT = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(APP_ROOT, '.env'))

class Config(object):
    SECRET_KEY = os.getenv('SECRET_KEY') or binascii.hexlify(os.urandom(24))
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL') or \
        'sqlite:///' + os.path.join(APP_ROOT, 'label_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_MAX_OVERFLOW = int(os.getenv('MAX_OVERFLOW'))
    MYSQL_DATABASE_CHARSET = 'utf8mb4'
    
