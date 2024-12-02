from werkzeug.http import HTTP_STATUS_CODES

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
import logging
import os
from logging.handlers import SMTPHandler, RotatingFileHandler
from redis import Redis
from rq import Queue

from config import Config

db = SQLAlchemy()
migrate = Migrate()
mail = Mail()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)

    app.redis = Redis.from_url(app.config['REDIS_URL'])
    app.task_queue = Queue('backend-api-tasks', connection=app.redis)

    from app.cli import bp as cli_bp
    app.register_blueprint(cli_bp)

    from app.api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api')

    @app.route('/')
    def hello_world():
        return '<p>Hello, World!</p>'
    
    @app.errorhandler(404)
    def not_found(e):
        if request.path.startswith('/api/'):
            payload = {
                'success': False,
                'message': HTTP_STATUS_CODES.get(404, 'Unknown error'),
                'data': {}
            }
            return payload, 404
        else :
            return '404 Not Found', 404
        
    @app.errorhandler(405)
    def method_not_allowed(e):
        if request.path.startswith('/api/'):
            payload = {
                'success': False,
                'message': HTTP_STATUS_CODES.get(405, 'Unknown error'),
                'data': {}
            }
            return payload, 405
        else :
            return '405 Method Not Allowed', 405
        
    if not app.debug and not app.testing:
        if app.config['MAIL_SERVER']:
            auth = None
            if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
                auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            secure = None
            if app.config['MAIL_USE_TLS']:
                secure = ()
            mail_handler = SMTPHandler(
                mailhost=(app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
                fromaddr='no-reply@' + app.config['MAIL_SERVER'],
                toaddrs=app.config['ADMINS'], subject='Server Failure',
                credentials=auth, secure=secure)
            mail_handler.setLevel(logging.ERROR)
            app.logger.addHandler(mail_handler)

        if not os.path.exists('logs'):
            os.mkdir('logs')
        file_handler = RotatingFileHandler('logs/server.log', maxBytes=10240, backupCount=10)
        file_handler.setFormatter(logging.Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        app.logger.setLevel(logging.INFO)
        app.logger.info('Server startup')

    return app

from app import models
