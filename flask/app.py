
from flask import Flask, send_file, jsonify, request
from config import Config
from models import db
from routes import bp as auth_bp, comment_bp
import subprocess

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    from routes import main as main_bluprint
    app.register_blueprint(main_bluprint)

    return app

