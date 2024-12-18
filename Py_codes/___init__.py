from flask import Flask, request, render_template, redirect
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
import os
from os import path

db = SQLAlchemy()
DB_NAME = "database.db"

def create_app():
    app = Flask(__name__, static_folder="static")
    app.secret_key = 'fdfsd dsdgfs'
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{DB_NAME}'
    app.config['UPLOAD_FOLDER'] = 'Website/static/uploads/'
    db.init_app(app)
    
    from .serv import serv
    from .auth import auth

    app.register_blueprint(serv, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')

    from .users_cl import User

    create_database(app);

    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app

def create_database(app):
    if not path.exists('website/' + DB_NAME):
        with app.app_context():
            db.create_all()
