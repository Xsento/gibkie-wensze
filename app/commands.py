from datetime import date

import click
from flask.cli import with_appcontext

from app.extensions import db
from app.services.calendar_service import create_trip


@click.command("init-db")
@with_appcontext
def init_db_command():
    db.drop_all()
    db.create_all()
    create_trip("Majówka w Tatrach", date(2026, 10, 1), date(2027, 2, 28), "Tomasz", ["Arkadiusz", "Paweł"])
    click.echo("Do dupy ta baza ale dziala.")
