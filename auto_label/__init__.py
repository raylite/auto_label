from flask import Flask
from config import Config, DevelopmentConfig, ProductionConfig, TestingConfig
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
import logging
from logging.handlers import RotatingFileHandler
from flask_bootstrap import Bootstrap
from flask_debugtoolbar import DebugToolbarExtension
from flask_session import Session
import os


db = SQLAlchemy()
migrate = Migrate()
bootstrap = Bootstrap()
sess = Session()
toolbar = DebugToolbarExtension()

def create_app(config_class = Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    if app.config["ENV"] == "production":
        config_class = ProductionConfig
    elif app.config["ENV"] == "testing":
        config_class = TestingConfig
    else:
        config_class = DevelopmentConfig
    
    app.config.from_object(config_class)
    
    db.init_app(app)
    migrate.init_app(app, db)
    bootstrap.init_app(app)
    sess.init_app(app)
    toolbar.init_app(app)
    
    from auto_label.errors import bp as errors_bp
    app.register_blueprint(errors_bp, url_prefix='/error')
    
    from auto_label.main import bp as main_bp
    app.register_blueprint(main_bp)
    
    from auto_label.auth import bp as auth_bp
    app.register_blueprint(auth_bp)
    
    
    if not app.debug:
        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/labeller.log', maxBytes=10240,
                                           backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
    
        app.logger.setLevel(logging.INFO)
    
        app.logger.info('Labeller startup')
    return app



from auto_label import models