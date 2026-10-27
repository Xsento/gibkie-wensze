import os
from flask import Flask
from app.extensions import db

def create_app(test_config=None):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev"
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
        'DATABASE_URL',
        'postgresql+psycopg2://gibki_wonsz:januszpawlacz@localhost:5432/tripforge_db'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    if test_config:
        app.config.update(test_config)

    db.init_app(app)

    with app.app_context():
        from app import models

    from .routes import auth, calendar, costs, main, schedule, voting
    for module in (main, auth, calendar, voting, schedule, costs):
        app.register_blueprint(module.bp)

    from app.commands import init_db_command
    app.cli.add_command(init_db_command)

    return app
