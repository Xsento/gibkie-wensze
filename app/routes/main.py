from flask import Blueprint, current_app, flash, g, redirect, render_template, request, url_for

from app.forms import DayForm, RangeForm
from app.routes.calendar import current_member_id
from app.services import calendar_service
from app.services.calendar_service import CalendarError

bp = Blueprint("main", __name__)


@bp.route("/")
def index():
    if not g.user and not current_app.config["ALLOW_ACT_AS"]:
        return redirect(url_for("auth.login"))
    member_id = current_member_id()
    if g.user and member_id is None:
        return render_template("index.html", view=None, form=DayForm(), range_form=RangeForm())
    try:
        view = calendar_service.get_calendar(member_id,
                                             request.args.get("rok", type=int),
                                             request.args.get("miesiac", type=int),
                                             request.args.get("wyjazd", type=int))
    except CalendarError as e:
        flash(str(e), "danger")
        view = None
    user = g.user or ({"name": view.user_name} if view else None)
    return render_template("index.html", view=view, form=DayForm(), range_form=RangeForm(), user=user)
