# /flask_app/__init__.py

from flask import Flask
from flask_app.routes.auth import auth_bp
from flask_app.routes.events import events_bp
from flask_app.routes.availability import avail_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = 'devsecretkey'

    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(avail_bp)

    return app
