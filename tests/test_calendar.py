from datetime import date

import pytest

from app import create_app
from app.extensions import db
from app.services import calendar_service
from app.services.calendar_service import CalendarError

ORGANIZATOR, TOMASZ, PAWEL, OLA = 1, 2, 3, 4


@pytest.fixture
def app(tmp_path):
    app = create_app({"TESTING": True, "WTF_CSRF_ENABLED": False,
                      "SQLALCHEMY_DATABASE_URI": f"sqlite:///{tmp_path / 'test.db'}"})
    with app.app_context():
        db.create_all()
        # okno wyjazdu: 1 września – 31 października 2026
        calendar_service.create_trip("Majówka", date(2026, 9, 1), date(2026, 10, 31),
                                     "Arek", ["Tomasz", "Paweł", "Ola"])
    return app


def day_of(view, d):
    return next(x for week in view.weeks for x in week if x.day == d)


def test_month_grid_starts_on_monday(app):
    # wrzesień 2026 zaczyna się we wtorek, więc poniedziałek to 31 sierpnia
    with app.app_context():
        view = calendar_service.get_calendar(TOMASZ, 2026, 9)
    first_week = view.weeks[0]
    assert view.month_label == "Wrzesień 2026"
    assert [d.day.day for d in first_week] == [31, 1, 2, 3, 4, 5, 6]
    assert not first_week[0].in_month and first_week[1].in_month
    assert all(len(week) == 7 for week in view.weeks)
    assert view.weeks[-1][-1].day == date(2026, 10, 4)  # ostatni tydzień kończy się w niedzielę


def test_default_month_and_navigation(app):
    with app.app_context():
        view = calendar_service.get_calendar(TOMASZ)
        assert (view.year, view.month) == (2026, 9)  # domyślnie miesiąc początku okna
        assert view.prev_month == (2026, 8) and view.next_month == (2026, 10)
        december = calendar_service.get_calendar(TOMASZ, 2026, 12)
        assert december.next_month == (2027, 1)
        assert not any(d.in_window for week in december.weeks for d in week)


def test_toggle_and_levels(app):
    # kryterium akceptacji US-1: po wybraniu dnia rośnie licznik dostępnych osób
    d = date(2026, 9, 18)
    with app.app_context():
        calendar_service.toggle_day(TOMASZ, d)
        assert day_of(calendar_service.get_calendar(TOMASZ, 2026, 9), d).level == "few"
        calendar_service.toggle_day(PAWEL, d)
        assert day_of(calendar_service.get_calendar(TOMASZ, 2026, 9), d).level == "most"
        calendar_service.toggle_day(OLA, d)
        view = calendar_service.get_calendar(TOMASZ, 2026, 9)
        assert day_of(view, d).available_count == 3 and day_of(view, d).level == "all"
        assert day_of(view, d).mine and view.participants_count == 3 and view.members_count == 4
        calendar_service.toggle_day(OLA, d)  # odznaczenie
        assert day_of(calendar_service.get_calendar(TOMASZ, 2026, 9), d).available_count == 2


def test_organizer_approves_but_does_not_mark(app):
    with app.app_context():
        with pytest.raises(CalendarError):
            calendar_service.toggle_day(ORGANIZATOR, date(2026, 9, 18))
        with pytest.raises(CalendarError):
            calendar_service.approve_range(TOMASZ, date(2026, 9, 18), date(2026, 9, 21))
        calendar_service.approve_range(ORGANIZATOR, date(2026, 9, 18), date(2026, 9, 21))
        view = calendar_service.get_calendar(TOMASZ)
        assert view.approved_label == "18–21 września"
        assert day_of(view, date(2026, 9, 21)).approved and not day_of(view, date(2026, 9, 22)).approved
        calendar_service.approve_range(ORGANIZATOR, date(2026, 9, 30), date(2026, 10, 2))
        view = calendar_service.get_calendar(TOMASZ)
        assert view.approved_label == "30 września – 2 października"


@pytest.mark.parametrize("start, end", [
    (date(2026, 9, 21), date(2026, 9, 18)),  # odwrócony zakres
    (date(2026, 10, 30), date(2026, 11, 2)),  # poza oknem
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
        calendar_service.create_trip(title, start, end, "Arek")


def test_errors(app):
    with app.app_context():
        with pytest.raises(CalendarError):
            calendar_service.toggle_day(TOMASZ, date(2026, 11, 1))  # poza oknem
        with pytest.raises(CalendarError):
            calendar_service.get_calendar(99)  # nie ma takiego uczestnika


def test_routes(app):
    client = app.test_client()
    assert client.get("/kalendarz/").status_code == 302  # nie wybrano uczestnika
    client.get("/kalendarz/jako/2")
    assert client.get("/kalendarz/?rok=2026&miesiac=10").status_code == 200
    r = client.post("/kalendarz/toggle", data={"day": "2026-10-05"})
    assert r.headers["Location"].endswith("/kalendarz/?rok=2026&miesiac=10")
    with app.app_context():
        assert day_of(calendar_service.get_calendar(TOMASZ, 2026, 10), date(2026, 10, 5)).available_count == 1

    client.get("/kalendarz/jako/1")
    client.post("/kalendarz/zatwierdz", data={"start_date": "2026-10-05", "end_date": "2026-10-08"})
    with app.app_context():
        assert calendar_service.get_calendar(TOMASZ).approved_label == "5–8 października"


def test_init_db(app):
    result = app.test_cli_runner().invoke(args=["init-db"])
    assert "Gotowe" in result.output
