from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from app.forms import DayForm, RangeForm
from app.services import calendar_service
from app.services.calendar_service import CalendarError

bp = Blueprint("calendar", __name__, url_prefix="/kalendarz")


def flash_errors(form):
    for errors in form.errors.values():
        for error in errors:
            flash(error, "danger")


def back_to(day):
    if day:
        return redirect(url_for("calendar.show", rok=day.year, miesiac=day.month))
    return redirect(url_for("calendar.show"))


@bp.route("/")
def show():
    try:
        view = calendar_service.get_calendar(session.get("member_id"),
                                             request.args.get("rok", type=int),
                                             request.args.get("miesiac", type=int))
    except CalendarError as e:
        flash(str(e), "danger")
        return redirect(url_for("main.index"))
    return render_template("calendar-test.html", view=view, form=DayForm(), range_form=RangeForm())


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
    return redirect(url_for("calendar.show"))
