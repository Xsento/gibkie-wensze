from flask import Blueprint, flash, render_template, request, session

from app.forms import DayForm, RangeForm
from app.services import calendar_service
from app.services.calendar_service import CalendarError

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    try:
        view = calendar_service.get_calendar(session.get("member_id"),
                                             request.args.get("rok", type=int),
                                             request.args.get("miesiac", type=int))
    except CalendarError as e:
        flash(str(e), "danger")
        view = None
    return render_template("index.html", view=view, form=DayForm(), range_form=RangeForm())
