from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from datetime import timedelta 

db=SQLAlchemy()
login_manager=LoginManager()

def create_app():
    app= Flask(__name__)
    app.config["SECRET_KEY"]='secret_key'
    app.config["SQLALCHEMY_DATABASE_URI"]='sqlite:///vehicle-parking.db'
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"]=False 

    app.permanent_session_lifetime=timedelta(hours=1)

    db.init_app(app)
    login_manager.init_app(app)


    from .routes import main 
    app.register_blueprint(main)

    return(app)



