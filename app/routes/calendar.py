from flask import Blueprint, redirect, render_template, url_for

bp = Blueprint("calendar", __name__, url_prefix="/kalendarz")


@bp.route("/")
def show():
    return render_template("calendar.html")


@bp.route("/toggle", methods=["POST"])
def toggle():
    return redirect(url_for("calendar.show"))