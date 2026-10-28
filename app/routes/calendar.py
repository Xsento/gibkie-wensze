from flask import Blueprint, flash, redirect, session, url_for

from app.forms import DayForm, RangeForm
from app.services import calendar_service
from app.services.calendar_service import CalendarError

# Akcje kalendarza. Sam kalendarz wyświetla strona główna "/" (routes/main.py).
bp = Blueprint("calendar", __name__)


def flash_errors(form):
    for errors in form.errors.values():
        for error in errors:
            flash(error, "danger")


def back_to(day):
    if day:
        return redirect(url_for("main.index", rok=day.year, miesiac=day.month))
    return redirect(url_for("main.index"))


@bp.route("/toggle", methods=["POST"])
def toggle():
    form = DayForm()
    if form.validate_on_submit():
        try:
            calendar_service.toggle_day(session.get("member_id"), form.day.data)
        except CalendarError as e:
            flash(str(e), "danger")
    flash_errors(form)
    return back_to(form.day.data)


@bp.route("/zatwierdz", methods=["POST"])
def approve():
    form = RangeForm()
    if form.validate_on_submit():
        try:
            calendar_service.approve_range(session.get("member_id"), form.start_date.data, form.end_date.data)
            flash("Termin zatwierdzony.", "success")
        except CalendarError as e:
            flash(str(e), "danger")
    flash_errors(form)
    return back_to(form.start_date.data)


@bp.route("/jako/<int:member_id>")
def act_as(member_id):
    session["member_id"] = member_id
    return redirect(url_for("main.index"))
