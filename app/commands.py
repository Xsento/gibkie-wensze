import os
import secrets
from datetime import date

import click
from flask.cli import with_appcontext

from app.extensions import db
from app.models import User
from app.services.calendar_service import create_trip

DEMO_USERS = [
    ("Tomasz", "tomasz@tripforge.local"),
    ("Arkadiusz", "arkadiusz@tripforge.local"),
    ("Paweł", "pawel@tripforge.local"),
]


def _seed_user(name, email, password):
    user = User(name=name, email=email)
    user.set_password(password)
    db.session.add(user)
    return user


@click.command("init-db")
@with_appcontext
def init_db_command():
    db.drop_all()
    db.create_all()
    password = os.getenv("SEED_PASSWORD") or secrets.token_urlsafe(12)
    if not os.getenv("SEED_PASSWORD"):
        click.echo(f"Hasło kont demo (SEED_PASSWORD pozwala podać własne): {password}")
    tomasz, arkadiusz, pawel = (_seed_user(name, email, password) for name, email in DEMO_USERS)
    db.session.commit()
    create_trip("Majówka w Tatrach", date(2026, 10, 1), date(2027, 2, 28), tomasz, [arkadiusz, pawel])
    click.echo("Gotowe. Do dupy ta baza ale dziala.")