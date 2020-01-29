from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from server.config import Config
from flask_login import LoginManager
from flask_marshmallow import Marshmallow
import psycopg2

#init app



db = SQLAlchemy()
ma = Marshmallow()
login_manager = LoginManager()


def creat_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)
    login_manager.init_app(app)
    ma.init_app(app)
    
    from server.users.routes import users
    from server.label.routes import labels
    from server.notes.routes import notes
    app.register_blueprint(users)
    app.register_blueprint(labels)
    app.register_blueprint(notes)
    return app
