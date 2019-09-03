import os#, binascii
from dotenv import load_dotenv
import redis

APP_ROOT = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(APP_ROOT, '.env'))

class Config(object):
    DEBUG = False
    TESTING = False
    SECRET_KEY = b'c55cd4aa79141c551bd9cfb2e28d64de7c3e5b08ff6cdf6f'#os.getenv('SECRET_KEY')#or binascii.hexlify(os.urandom(24))
    SQLALCHEMY_DATABASE_URI = f"{os.getenv('DATABASE_URL')}{os.getenv('DB_ADMIN')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}/{os.getenv('DB_NAME')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_MAX_OVERFLOW = int(os.getenv('MAX_OVERFLOW'))
    MYSQL_DATABASE_CHARSET = 'utf8mb4'
    DATA_FOLDER = os.path.join(APP_ROOT, 'data')
    REDIRECT_URI = os.getenv('REDIRECT_URI')
    SESSION_REDIS = redis.from_url(os.getenv('REDIS_URI'))
    SESSION_TYPE = os.getenv('SESSION_TYPE')
    SESSION_COOKIE_SECURE = False
    MAX_LABEL_ROUND_PER_ARTICLE = int(os.getenv('MAX_ROUND'))
    
    
    
    
class ProductionConfig(Config):
    REDIRECT_URI = os.getenv('PRODUCTION_REDIRECT_URI')
    SESSION_COOKIE_SECURE = True
    
class DevelopmentConfig(Config):
    DEBUG = True
    DEBUG_TB_INTERCEPT_REDIRECTS = os.getenv('INTERCEPT_REDIRECTS')##for debug toolbar
    DEBUG_TB_PROFILER_ENABLED = os.getenv('PROFILER_ENABLED')
    
class TestingConfig(Config):
    Testing = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
