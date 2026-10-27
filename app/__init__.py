import os
from flask import Flask
from app.extensions import db

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'postgresql://gibki_wonsz:januszpawlacz@localhost:5432/tripforge_db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)

    with app.app_context():
        from app import models

    from .routes import auth, calendar, costs, main, schedule, voting
    for module in (main, auth, calendar, voting, schedule, costs):
        app.register_blueprint(module.bp)

    return app
