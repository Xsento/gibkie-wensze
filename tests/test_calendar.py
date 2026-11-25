from datetime import date

import pytest

from app import create_app
from app.extensions import db
from app.models import User
from app.services import calendar_service
from app.services.calendar_service import CalendarError

ORGANIZATOR, TOMASZ, PAWEL, OLA = 1, 2, 3, 4


@pytest.fixture
def app(tmp_path):
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False,
                      "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}"})
    with app.app_context():
        db.create_all()
        users = [make_user(name) for name in ("Arek", "Tomasz", "Paweł", "Ola")]
        calendar_service.create_trip("Majówka", date(2026, 9, 1), date(2026, 10, 31),
                                     users[0], users[1:])
    return app


def make_user(name):
    user = User(name=name, email=f"{name.lower()}@test.local")
    user.set_password("test")
    db.session.add(user)
    db.session.commit()
    return user


def day_of(view, d):
    return next(x for week in view.weeks for x in week if x.day == d)


def test_month_grid_starts_on_monday(app):
    with app.app_context():
        view = calendar_service.get_calendar(TOMASZ, 2026, 9)
    first_week = view.weeks[0]
    assert view.month_label == "Wrzesień 2026"
    assert [d.day.day for d in first_week] == [31, 1, 2, 3, 4, 5, 6]
    assert not first_week[0].in_month and first_week[1].in_month
    assert all(len(week) == 7 for week in view.weeks)
    assert view.weeks[-1][-1].day == date(2026, 10, 4)


def test_default_month_and_navigation(app):
    with app.app_context():
        view = calendar_service.get_calendar(TOMASZ)
        assert (view.year, view.month) == (2026, 9)
        assert view.prev_month == (2026, 8) and view.next_month == (2026, 10)
        december = calendar_service.get_calendar(TOMASZ, 2026, 12)
        assert december.next_month == (2027, 1)
        assert not any(d.in_window for week in december.weeks for d in week)


def test_toggle_and_levels(app):
    d = date(2026, 9, 18)
    with app.app_context():
        calendar_service.toggle_day(TOMASZ, d)
        calendar_service.toggle_day(PAWEL, d)
        assert day_of(calendar_service.get_calendar(TOMASZ, 2026, 9), d).level == "few"
        calendar_service.toggle_day(OLA, d)
        assert day_of(calendar_service.get_calendar(TOMASZ, 2026, 9), d).level == "most"
        calendar_service.toggle_day(ORGANIZATOR, d)
        view = calendar_service.get_calendar(TOMASZ, 2026, 9)
        assert day_of(view, d).available_count == 4 and day_of(view, d).level == "all"
        assert day_of(view, d).share == 1.0 and day_of(view, date(2026, 9, 19)).share == 0.0
        assert day_of(view, d).mine and view.members_count == 4
        calendar_service.toggle_day(OLA, d)
        assert day_of(calendar_service.get_calendar(TOMASZ, 2026, 9), d).available_count == 3
        assert day_of(calendar_service.get_calendar(TOMASZ, 2026, 9), d).share == 0.75


def test_organizer_marks_and_approves(app):
    with app.app_context():
        calendar_service.toggle_day(ORGANIZATOR, date(2026, 9, 18))
        assert day_of(calendar_service.get_calendar(ORGANIZATOR, 2026, 9), date(2026, 9, 18)).mine
        with pytest.raises(CalendarError):
            calendar_service.approve_range(TOMASZ, date(2026, 9, 18), date(2026, 9, 21))
        calendar_service.approve_range(ORGANIZATOR, date(2026, 9, 18), date(2026, 9, 21))
        view = calendar_service.get_calendar(TOMASZ)
        assert view.approved_label == "18–21 września"
        assert day_of(view, date(2026, 9, 21)).approved and not day_of(view, date(2026, 9, 22)).approved
        assert view.locked


def test_approved_range_locks_calendar(app):
    with app.app_context():
        assert not calendar_service.get_calendar(TOMASZ).locked
        calendar_service.toggle_day(TOMASZ, date(2026, 9, 18))
        calendar_service.approve_range(ORGANIZATOR, date(2026, 9, 30), date(2026, 10, 2))
        view = calendar_service.get_calendar(TOMASZ)
        assert view.locked and view.approved_label == "30 września – 2 października"
        for member in (TOMASZ, PAWEL, ORGANIZATOR):
            with pytest.raises(CalendarError):
                calendar_service.toggle_day(member, date(2026, 9, 18))
        with pytest.raises(CalendarError):
            calendar_service.approve_range(ORGANIZATOR, date(2026, 9, 18), date(2026, 9, 21))
        view = calendar_service.get_calendar(TOMASZ)
        assert day_of(view, date(2026, 9, 18)).available_count == 1
        assert view.approved_label == "30 września – 2 października"


@pytest.mark.parametrize("start, end", [
    (date(2026, 9, 21), date(2026, 9, 18)),
    (date(2026, 10, 30), date(2026, 11, 2)),
])
def test_approve_validation(app, start, end):
    with app.app_context(), pytest.raises(CalendarError):
        calendar_service.approve_range(ORGANIZATOR, start, end)


@pytest.mark.parametrize("title, start, end", [
    ("", date(2026, 5, 1), date(2026, 5, 3)),
    ("Majówka", date(2026, 5, 3), date(2026, 5, 1)),
    ("Majówka", date(2026, 1, 1), date(2026, 6, 30)),
])
def test_create_trip_validation(app, title, start, end):
    with app.app_context(), pytest.raises(CalendarError):
        calendar_service.create_trip(title, start, end, db.session.get(User, 1))


def test_errors(app):
    with app.app_context():
        with pytest.raises(CalendarError):
            calendar_service.toggle_day(TOMASZ, date(2026, 11, 1))
        with pytest.raises(CalendarError):
            calendar_service.get_calendar(99)


def test_routes(app):
    client = app.test_client()
    r = client.get("/")
    assert r.status_code == 200 and "Wybierz uczestnika" in r.get_data(as_text=True)
    client.get("/jako/2")
    page = client.get("/?rok=2026&miesiac=10").get_data(as_text=True)
    assert "Październik 2026" in page
    r = client.post("/toggle", data={"day": "2026-10-05"})
    assert r.headers["Location"].endswith("/?rok=2026&miesiac=10")
    with app.app_context():
        assert day_of(calendar_service.get_calendar(TOMASZ, 2026, 10), date(2026, 10, 5)).available_count == 1

    client.get("/jako/1")
    client.post("/toggle", data={"day": "2026-10-05"})
    client.post("/zatwierdz", data={"start_date": "2026-10-05", "end_date": "2026-10-08"})
    with app.app_context():
        view = calendar_service.get_calendar(TOMASZ)
        assert view.approved_label == "5–8 października"
        assert day_of(view, date(2026, 10, 5)).available_count == 2

    page = client.get("/?rok=2026&miesiac=10").get_data(as_text=True)
    assert "tf-calendar-button" not in page and "Zatwierdź termin" not in page
    assert "Zatwierdzono 5–8 października" in page
    r = client.post("/toggle", data={"day": "2026-10-06"}, follow_redirects=True)
    assert "Termin jest już zatwierdzony" in r.get_data(as_text=True)


def test_init_db(app):
    result = app.test_cli_runner().invoke(args=["init-db"])
    assert "Gotowe" in result.output
