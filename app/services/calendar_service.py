# Logika biznesowa US-1: zaznaczanie dostępności i zatwierdzanie terminu.
import calendar
from dataclasses import dataclass
from datetime import date

from app.models import Availability
from app.repositories import calendar_repository as repo

MAX_WINDOW_DAYS = 180
MONTHS = ["Styczeń", "Luty", "Marzec", "Kwiecień", "Maj", "Czerwiec", "Lipiec",
          "Sierpień", "Wrzesień", "Październik", "Listopad", "Grudzień"]
MONTHS_GENITIVE = ["stycznia", "lutego", "marca", "kwietnia", "maja", "czerwca", "lipca",
                   "sierpnia", "września", "października", "listopada", "grudnia"]


class CalendarError(Exception):
    pass


@dataclass
class CalendarDay:
    day: date
    in_month: bool
    in_window: bool
    available_count: int
    level: str
    mine: bool
    approved: bool


@dataclass
class CalendarView:
    trip_id: int
    trip_title: str
    members_count: int
    participants_count: int
    is_organizer: bool
    year: int
    month: int
    month_label: str
    prev_month: tuple
    next_month: tuple
    weeks: list
    approved_label: str


def create_trip(title, start_date, end_date, organizer_name, member_names=()):
    title = (title or "").strip()
    if not title:
        raise CalendarError("Tytuł wyjazdu jest wymagany.")
    _check_range(start_date, end_date)
    if (end_date - start_date).days + 1 > MAX_WINDOW_DAYS:
        raise CalendarError(f"Okno dat może mieć najwyżej {MAX_WINDOW_DAYS} dni.")
    return repo.add_trip(title, start_date, end_date, organizer_name, member_names)


def get_calendar(member_id, year=None, month=None):
    member = _get_member(member_id)
    trip = member.trip
    if year is None or month is None or not 1 <= month <= 12:
        start = trip.approved_start or trip.start_date
        year, month = start.year, start.month

    counts = repo.count_available_by_day(trip.id)
    mine = repo.available_days_of_member(member.id)
    participants = repo.count_members(trip.id, organizers=False)

    weeks = []
    for week in calendar.Calendar(firstweekday=0).monthdatescalendar(year, month):
        weeks.append([
            CalendarDay(
                day=d,
                in_month=d.month == month,
                in_window=trip.start_date <= d <= trip.end_date,
                available_count=counts.get(d, 0),
                level=_level(counts.get(d, 0), participants),
                mine=d in mine,
                approved=bool(trip.approved_start) and trip.approved_start <= d <= trip.approved_end,
            )
            for d in week
        ])

    return CalendarView(
        trip_id=trip.id,
        trip_title=trip.title,
        members_count=repo.count_members(trip.id),
        participants_count=participants,
        is_organizer=member.is_organizer,
        year=year,
        month=month,
        month_label=f"{MONTHS[month - 1]} {year}",
        prev_month=(year - 1, 12) if month == 1 else (year, month - 1),
        next_month=(year + 1, 1) if month == 12 else (year, month + 1),
        weeks=weeks,
        approved_label=_range_label(trip.approved_start, trip.approved_end),
    )


def toggle_day(member_id, day):
    member = _get_member(member_id)
    if member.is_organizer:
        raise CalendarError("Organizator nie zaznacza dostępności, tylko zatwierdza termin.")
    _check_in_window(member.trip, day, day)

    availability = repo.get_availability(member.id, day)
    if availability is None:
        availability = Availability(trip_member_id=member.id, day=day, state=True)
    else:
        availability.state = not availability.state
    repo.save(availability)


def approve_range(member_id, start, end):
    member = _get_member(member_id)
    if not member.is_organizer:
        raise CalendarError("Tylko organizator może zatwierdzić termin.")
    _check_range(start, end)
    trip = member.trip
    _check_in_window(trip, start, end)
    trip.approved_start, trip.approved_end = start, end
    repo.save(trip)


def _level(count, participants):
    if count == 0 or participants == 0:
        return ""
    if count >= participants:
        return "all"
    if count * 2 > participants:
        return "most"
    return "few"


def _range_label(start, end):
    if not start:
        return ""
    if start == end:
        return f"{start.day} {MONTHS_GENITIVE[start.month - 1]}"
    if (start.year, start.month) == (end.year, end.month):
        return f"{start.day}–{end.day} {MONTHS_GENITIVE[end.month - 1]}"
    return f"{start.day} {MONTHS_GENITIVE[start.month - 1]} – {end.day} {MONTHS_GENITIVE[end.month - 1]}"


def _check_range(start, end):
    if end < start:
        raise CalendarError("Data końcowa nie może być wcześniejsza niż początkowa.")


def _check_in_window(trip, start, end):
    if start < trip.start_date or end > trip.end_date:
        raise CalendarError(f"Wybierz dni od {trip.start_date:%d.%m.%Y} do {trip.end_date:%d.%m.%Y}.")


def _get_member(member_id):
    member = repo.get_member(member_id) if member_id else None
    if member is None:
        raise CalendarError("Nie jesteś uczestnikiem tego wyjazdu.")
    return member
