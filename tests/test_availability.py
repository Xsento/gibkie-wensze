# Testy UC: zaznaczanie dostępności uczestników wyjazdu grupowego w kalendarzu.
from datetime import date

import pytest
from sqlalchemy.exc import IntegrityError

from app import create_app
from app.extensions import db
from app.models import Availability, TripMember, User
from app.repositories import calendar_repository as repo
from app.services import calendar_service
from app.services.calendar_service import CalendarError

# wyjazd A: Arek (organizator), Tomasz, Paweł; wyjazd B: Ola (organizatorka), Tomasz
TRIP_A, TRIP_B = 1, 2
A_AREK, A_TOMASZ, A_PAWEL = 1, 2, 3
B_OLA, B_TOMASZ = 4, 5
DAY = date(2026, 9, 18)


def make_user(name):
    user = User(name=name, email=f"{name.lower()}@test.local")
    user.set_password("test")
    db.session.add(user)
    db.session.commit()
    return user


@pytest.fixture
def db_uri(tmp_path):
    return f"sqlite:///{tmp_path / 'test.db'}"


@pytest.fixture
def app(db_uri):
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False, "SQLALCHEMY_DATABASE_URI": db_uri})
    with app.app_context():
        db.create_all()
        arek, tomasz, pawel, ola = (make_user(n) for n in ("Arek", "Tomasz", "Pawel", "Ola"))
        calendar_service.create_trip("Majówka", date(2026, 9, 1), date(2026, 10, 31), arek, [tomasz, pawel])
        calendar_service.create_trip("Wrzesień nad morzem", date(2026, 9, 10), date(2026, 9, 30), ola, [tomasz])
    return app


def login_as(app, member_id):
    client = app.test_client()
    client.get(f"/jako/{member_id}")
    return client


def toggle(client, day=DAY, trip_id=TRIP_A, **extra):
    return client.post("/toggle", data={"day": day.isoformat(), "trip_id": trip_id, **extra})


def page(client, trip_id=TRIP_A, year=2026, month=9):
    return client.get(f"/?wyjazd={trip_id}&rok={year}&miesiac={month}").get_data(as_text=True)


def count(app, trip_id=TRIP_A, day=DAY, member_id=A_TOMASZ):
    with app.app_context():
        view = calendar_service.get_calendar(member_id, day.year, day.month, trip_id)
        return next(d for week in view.weeks for d in week if d.day == day).available_count


def saved_rows(app, member_id):
    with app.app_context():
        return [(a.day, a.state) for a in Availability.query.filter_by(trip_member_id=member_id).all()]


# 1. Uczestnik wyjazdu może otworzyć kalendarz swojego wyjazdu
def test_member_can_open_trip_calendar(app):
    client = login_as(app, A_TOMASZ)
    r = client.get(f"/?wyjazd={TRIP_A}&rok=2026&miesiac=9")
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    assert "Majówka" in html and "Wrzesień 2026" in html and "tf-calendar-button" in html
    # ten sam użytkownik otwiera też kalendarz drugiego wyjazdu, do którego należy
    html_b = page(client, TRIP_B)
    assert "Wrzesień nad morzem" in html_b and "tf-calendar-button" in html_b


# 2. Zaznaczenie dnia zapisuje dostępność w bazie danych
def test_toggle_saves_availability_in_db(app):
    r = toggle(login_as(app, A_TOMASZ))
    assert r.status_code == 302
    assert r.headers["Location"].endswith(f"/?wyjazd={TRIP_A}&rok=2026&miesiac=9")
    assert saved_rows(app, A_TOMASZ) == [(DAY, True)]
    with app.app_context():
        member = db.session.get(TripMember, A_TOMASZ)
        assert member.user.name == "Tomasz" and member.trip.title == "Majówka"


# 3. Ponowne kliknięcie dnia usuwa dostępność
def test_second_click_removes_availability(app):
    client = login_as(app, A_TOMASZ)
    toggle(client)
    toggle(client)
    with app.app_context():
        assert DAY not in repo.available_days_of_member(A_TOMASZ)
    assert count(app) == 0
    assert 'aria-pressed="true"' not in page(client)


# 4. Licznik dostępnych osób rośnie po zaznaczeniu dnia
def test_counter_increases(app):
    tomasz, pawel = login_as(app, A_TOMASZ), login_as(app, A_PAWEL)
    assert count(app) == 0
    toggle(tomasz)
    assert count(app) == 1
    toggle(pawel)
    assert count(app) == 2
    html = page(tomasz)
    assert "2/3" in html and "2 z 3 osób (w tym Ty): Pawel, Tomasz" in html
    # Paweł widzi dzień jako dostępny dla innych, a swój zaznaczony
    toggle(pawel, date(2026, 9, 20))
    html = page(tomasz)
    assert "1 z 3 osób: Pawel" in html


# 5. Licznik maleje po usunięciu dostępności
def test_counter_decreases(app):
    tomasz, pawel = login_as(app, A_TOMASZ), login_as(app, A_PAWEL)
    toggle(tomasz)
    toggle(pawel)
    assert count(app) == 2
    toggle(pawel)
    assert count(app) == 1
    assert "1/3" in page(tomasz)


# 6. Dostępność jednego użytkownika nie jest liczona wielokrotnie
def test_availability_not_counted_twice(app):
    client = login_as(app, A_TOMASZ)
    for _ in range(3):
        toggle(client)
    assert count(app) == 1
    assert saved_rows(app, A_TOMASZ) == [(DAY, True)]
    with app.app_context():
        # baza blokuje duplikat wpisu (uczestnik, dzień)
        db.session.add(Availability(trip_member_id=A_TOMASZ, day=DAY, state=True))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()
        # i ponowne dodanie tego samego użytkownika do wyjazdu
        db.session.add(TripMember(trip_id=TRIP_A, user_id=2, name="Tomasz"))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()
        tomasz = db.session.get(User, 2)
        with pytest.raises(CalendarError):
            calendar_service.create_trip("Dubel", date(2026, 9, 1), date(2026, 9, 5), tomasz, [tomasz])
    assert count(app) == 1


# 7. Dostępność jest przypisana do konkretnego wyjazdu
def test_availability_belongs_to_trip(app):
    client = login_as(app, A_TOMASZ)
    toggle(client, trip_id=TRIP_B)
    assert count(app, TRIP_B, member_id=B_OLA) == 1
    assert count(app, TRIP_A) == 0
    assert saved_rows(app, B_TOMASZ) == [(DAY, True)] and saved_rows(app, A_TOMASZ) == []
    toggle(client, trip_id=TRIP_A)
    assert count(app, TRIP_A) == 1 and count(app, TRIP_B, member_id=B_OLA) == 1


# 8. Użytkownik nie może zmienić dostępności innego uczestnika
def test_cannot_change_other_members_availability(app):
    toggle(login_as(app, A_TOMASZ))
    pawel = login_as(app, A_PAWEL)
    # próba podstawienia identyfikatora Tomasza w formularzu jest ignorowana
    toggle(pawel, member_id=A_TOMASZ, trip_member_id=A_TOMASZ, user_id=2)
    assert saved_rows(app, A_TOMASZ) == [(DAY, True)]
    assert saved_rows(app, A_PAWEL) == [(DAY, True)]
    assert count(app) == 2


# 9. Użytkownik spoza wyjazdu nie może modyfikować dostępności w tym wyjeździe
def test_outsider_cannot_modify_trip(app):
    toggle(login_as(app, A_TOMASZ))
    ola = login_as(app, B_OLA)
    r = toggle(ola, trip_id=TRIP_A)
    assert r.status_code == 302
    html = ola.get(r.headers["Location"]).get_data(as_text=True)
    assert "Nie jesteś uczestnikiem tego wyjazdu" in html and "Majówka" not in html
    assert count(app) == 1 and saved_rows(app, B_OLA) == []
    with app.app_context():
        with pytest.raises(CalendarError):
            calendar_service.toggle_day(B_OLA, DAY, TRIP_A)
        with pytest.raises(CalendarError):
            calendar_service.get_calendar(B_OLA, 2026, 9, TRIP_A)
    # niezalogowany też nie może nic zapisać
    anonymous = app.test_client()
    toggle(anonymous)
    assert count(app) == 1


# 10. Zapisane dane są dostępne po ponownym wejściu do kalendarza
def test_availability_persists(app, db_uri):
    toggle(login_as(app, A_TOMASZ))
    # nowa sesja przeglądarki
    html = page(login_as(app, A_TOMASZ))
    assert 'aria-pressed="true"' in html and "1/3" in html
    # nowa instancja aplikacji na tej samej bazie
    fresh = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False, "SQLALCHEMY_DATABASE_URI": db_uri})
    html = page(login_as(fresh, A_TOMASZ))
    assert 'aria-pressed="true"' in html and "1/3" in html


def test_toggle_requires_csrf_token(db_uri, app):
    secured = create_app({"TESTING": True, "SQLALCHEMY_DATABASE_URI": db_uri})
    toggle(login_as(secured, A_TOMASZ))
    assert saved_rows(app, A_TOMASZ) == []


def test_parallel_double_click_does_not_duplicate(app, monkeypatch):
    toggle(login_as(app, A_TOMASZ))
    # drugie żądanie „nie widzi” jeszcze wpisu z pierwszego i próbuje dodać nowy
    monkeypatch.setattr(repo, "get_availability", lambda member_id, day: None)
    with app.app_context():
        with pytest.raises(CalendarError):
            calendar_service.toggle_day(A_TOMASZ, DAY, TRIP_A)
    assert saved_rows(app, A_TOMASZ) == [(DAY, True)] and count(app) == 1
