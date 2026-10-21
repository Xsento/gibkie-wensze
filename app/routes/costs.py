from flask import Blueprint, render_template

bp = Blueprint("costs", __name__, url_prefix="/koszty")


@bp.route("/")
def show():
    return render_template("costs.html")