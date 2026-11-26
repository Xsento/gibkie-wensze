from flask import Blueprint, abort, current_app, flash, g, redirect, session, url_for

from app.forms import DayForm, RangeForm
from app.services import auth_service, calendar_service
from app.services.calendar_service import CalendarError

bp = Blueprint("calendar", __name__)


def current_member_id():
    # zalogowany użytkownik (US-5); konkretny wyjazd wskazuje trip_id / ?wyjazd=
    if g.get("user"):
        return auth_service.default_member_id(g.user.id)
    if current_app.config["ALLOW_ACT_AS"]:
        return session.get("member_id")
    return None


def flash_errors(form):
    for errors in form.errors.values():
        for error in errors:
            flash(error, "danger")


def back_to(day, trip_id=None):
    if day:
        return redirect(url_for("main.calendar", wyjazd=trip_id, rok=day.year, miesiac=day.month))
    return redirect(url_for("main.calendar", wyjazd=trip_id))


@bp.route("/toggle", methods=["POST"])
def toggle():
    form = DayForm()
    if form.validate_on_submit():
        try:
            calendar_service.toggle_day(current_member_id(), form.day.data, form.trip_id.data)
        except CalendarError as e:
            flash(str(e), "danger")
    flash_errors(form)
    return back_to(form.day.data, form.trip_id.data)


@bp.route("/zatwierdz", methods=["POST"])
def approve():
    form = RangeForm()
    if form.validate_on_submit():
        try:
            calendar_service.approve_range(current_member_id(), form.start_date.data, form.end_date.data,
                                           form.trip_id.data)
            flash("Termin zatwierdzony.", "success")
        except CalendarError as e:
            flash(str(e), "danger")
    flash_errors(form)
    return back_to(form.start_date.data, form.trip_id.data)


@bp.route("/jako/<int:member_id>")
def act_as(member_id):
    if not current_app.config["ALLOW_ACT_AS"]:
        abort(404)
    session.pop("user_id", None)
    session["member_id"] = member_id
    return redirect(url_for("main.calendar"))
