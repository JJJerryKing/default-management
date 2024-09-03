from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
import sys
sys.path.append(current_dir)
from config import Config
from models import db
 
 
# 在app.config中设置好连接数据库的信息，
# 然后使用SQLAlchemy(app)创建一个db对象
# SQLAlchemy会自动读取app.config中连接数据库的信息


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    # 在app.config中设置好连接数据库的信息，
    # 然后使用SQLAlchemy(app)创建一个db对象
    # SQLAlchemy会自动读取app.config中连接数据库的信息
    db.init_app(app)

    with app.app_context():
        db.reflect()
        db.drop_all()
        # Import models here to ensure they are registered with SQLAlchemy
        from models import DefaultApplication, Customer, DefaultRebirth
        db.create_all()

    return app

app = create_app()