from datetime import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask import request
import logging
from logging.handlers import RotatingFileHandler
import os

from config.config import Config
from config.db import db
from routes.auth import auth_bp
from routes.news import news_bp
from routes.admin import admin_bp
from utils.error_handler import error_handler, not_found, internal_server_error


def create_app():
    """Application factory"""
    app = Flask(__name__)

    # Configuration
    app.config['JWT_SECRET_KEY'] = Config.JWT_SECRET
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = Config.JWT_ACCESS_TOKEN_EXPIRES

    # CORS
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # JWT
    jwt = JWTManager(app)

    # Setup logging
    if not os.path.exists('logs'):
        os.mkdir('logs')

    file_handler = RotatingFileHandler('logs/app.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.INFO)
    app.logger.info('Fake News Detection System startup')

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(admin_bp)

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'success': True,
            'message': 'API is running',
            'timestamp': datetime.utcnow().isoformat()
        }), 200

    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            'success': True,
            'message': 'Fake News Detection API',
            'version': '1.0.0'
        })

    # Error handlers
    app.register_error_handler(404, not_found)
    app.register_error_handler(500, internal_server_error)
    app.errorhandler(Exception)(error_handler)

    # JWT error handling
    @jwt.expired_token_loader
    def expired_token_callback(jwt_header, jwt_payload):
        return jsonify({
            'success': False,
            'message': 'Token has expired'
        }), 401

    @jwt.invalid_token_loader
    def invalid_token_callback(error):
        return jsonify({
            'success': False,
            'message': 'Invalid token'
        }), 401

    @jwt.unauthorized_loader
    def missing_token_callback(error):
        return jsonify({
            'success': False,
            'message': 'Authorization token required'
        }), 401

    return app


app = create_app()

if __name__ == '__main__':
    # Create logs directory
    if not os.path.exists('logs'):
        os.mkdir('logs')

    app.run(
        host='0.0.0.0',
        port=Config.PORT,
        debug=(Config.FLASK_ENV == 'development')
    )