# Testy US-5: rejestracja, logowanie i wylogowanie.
from datetime import date

import pytest

from app import create_app
from app.extensions import db
from app.models import Availability, TripMember, User
from app.services import calendar_service

PASSWORD = "tajnehaslo1"


@pytest.fixture
def db_uri(tmp_path):
    return f"sqlite:///{tmp_path / 'test.db'}"


@pytest.fixture
def app(db_uri):
    # ALLOW_ACT_AS=False: tożsamość wyłącznie z logowania, bez /jako/<id>
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False, "ALLOW_ACT_AS": False,
                      "SQLALCHEMY_DATABASE_URI": db_uri})
    with app.app_context():
        db.create_all()
        users = []
        for name in ("Arek", "Tomasz"):
            user = User(name=name, email=f"{name.lower()}@test.local")
            user.set_password(PASSWORD)
            db.session.add(user)
            users.append(user)
        db.session.commit()
        calendar_service.create_trip("Majówka", date(2026, 9, 1), date(2026, 10, 31), users[0], users[1:])
    return app


def login(client, email="tomasz@test.local", password=PASSWORD):
    return client.post("/login", data={"email": email, "password": password})


def register(client, **overrides):
    data = {"name": "Ola", "email": "ola@test.local", "password": PASSWORD, "confirm": PASSWORD, **overrides}
    return client.post("/rejestracja", data=data)


def test_login_and_register_pages_render(app):
    client = app.test_client()
    login_page = client.get("/login").get_data(as_text=True)
    assert 'name="email"' in login_page and 'type="password"' in login_page and "<form" in login_page
    register_page = client.get("/rejestracja").get_data(as_text=True)
    assert 'name="name"' in register_page and 'name="confirm"' in register_page
    assert "class=" not in login_page and "class=" not in register_page  # plain HTML


def test_register_creates_user_with_hashed_password(app):
    client = app.test_client()
    r = register(client, email="  Ola@Test.local ")
    assert r.status_code == 302 and r.headers["Location"].endswith("/")
    with app.app_context():
        user = User.query.filter_by(email="ola@test.local").one()
        assert user.name == "Ola" and user.password_hash != PASSWORD and user.check_password(PASSWORD)
    # od razu zalogowany; nie należy jeszcze do żadnego wyjazdu
    page = client.get("/").get_data(as_text=True)
    assert "Ola" in page and "Nie należysz jeszcze do żadnego wyjazdu" in page


@pytest.mark.parametrize("overrides, message", [
    ({"email": "tomasz@test.local"}, "Konto z tym adresem e-mail już istnieje."),
    ({"email": "TOMASZ@test.local"}, "Konto z tym adresem e-mail już istnieje."),
    ({"confirm": "inne-haslo"}, "Hasła nie są takie same."),
    ({"password": "krotkie", "confirm": "krotkie"}, "Hasło musi mieć co najmniej 8 znaków."),
    ({"email": "bez-malpy"}, "Podaj poprawny adres e-mail."),
    ({"name": ""}, "Podaj imię."),
])
def test_register_validation(app, overrides, message):
    client = app.test_client()
    r = register(client, **overrides)
    assert r.status_code == 200 and message in r.get_data(as_text=True)
    with app.app_context():
        assert User.query.count() == 2


def test_login_success_redirects_to_own_calendar(app):
    client = app.test_client()
    r = login(client, email="Tomasz@test.local")
    assert r.status_code == 302 and r.headers["Location"].endswith("/")
    page = client.get("/").get_data(as_text=True)
    assert "Majówka" in page and "Tomasz" in page and "Wyloguj" in page


@pytest.mark.parametrize("email, password", [
    ("tomasz@test.local", "zle-haslo"),
    ("nieznany@test.local", PASSWORD),
])
def test_login_failure_shows_error(app, email, password):
    client = app.test_client()
    r = login(client, email, password)
    assert r.status_code == 200 and "Nieprawidłowy e-mail lub hasło." in r.get_data(as_text=True)
    assert client.get("/").headers["Location"].endswith("/login")


def test_logged_in_user_toggles_own_availability(app):
    client = app.test_client()
    login(client)
    client.post("/toggle", data={"day": "2026-09-18", "trip_id": 1})
    with app.app_context():
        rows = Availability.query.all()
        assert len(rows) == 1 and rows[0].member.user.email == "tomasz@test.local"
    assert "1/2" in client.get("/?wyjazd=1&rok=2026&miesiac=9").get_data(as_text=True)


def test_logout_and_anonymous_access(app):
    client = app.test_client()
    login(client)
    r = client.get("/logout")
    assert r.headers["Location"].endswith("/login")
    assert client.get("/").headers["Location"].endswith("/login")
    client.post("/toggle", data={"day": "2026-09-18", "trip_id": 1})
    with app.app_context():
        assert Availability.query.count() == 0


def test_act_as_disabled_without_flag(app):
    assert app.test_client().get("/jako/1").status_code == 404


def test_login_requires_csrf_token(db_uri, app):
    secured = create_app({"TESTING": True, "ALLOW_ACT_AS": False, "SQLALCHEMY_DATABASE_URI": db_uri})
    client = secured.test_client()
    r = login(client)
    assert r.status_code == 200
    assert client.get("/").headers["Location"].endswith("/login")


def test_init_db_accounts_can_log_in(tmp_path, monkeypatch):
    fresh = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False, "ALLOW_ACT_AS": False,
                        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'demo.db'}"})
    runner = fresh.test_cli_runner()

    # bez SEED_PASSWORD hasło jest losowe i wypisane w konsoli
    monkeypatch.delenv("SEED_PASSWORD", raising=False)
    output = runner.invoke(args=["init-db"]).output
    password = output.split("podać własne): ")[1].split()[0]
    client = fresh.test_client()
    login(client, "pawel@tripforge.local", password)
    page = client.get("/").get_data(as_text=True)
    assert "Majówka w Tatrach" in page and "Paweł" in page and "tf-calendar-button" in page

    # z SEED_PASSWORD konta dostają podane hasło i nic nie jest wypisywane
    monkeypatch.setenv("SEED_PASSWORD", "haslo-z-env")
    output = runner.invoke(args=["init-db"]).output
    assert "haslo-z-env" not in output and "Gotowe" in output
    with fresh.app_context():
        assert User.query.count() == 3 and TripMember.query.count() == 3
        assert all(u.check_password("haslo-z-env") for u in User.query.all())
