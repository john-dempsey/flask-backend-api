from werkzeug.http import HTTP_STATUS_CODES

from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from config import Config

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

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
        
    @app.errorhandler(405)
    def method_not_allowed(e):
        if request.path.startswith('/api/'):
            payload = {
                'success': False,
                'message': HTTP_STATUS_CODES.get(405, 'Unknown error'),
                'data': {}
            }
            return payload, 405
        
    return app

from app import models
