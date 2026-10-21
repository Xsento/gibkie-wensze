from flask import Blueprint, redirect, render_template, url_for

bp = Blueprint("schedule", __name__, url_prefix="/harmonogram")


@bp.route("/")
def show():
    return render_template("schedule.html")


@bp.route("/dodaj", methods=["POST"])
def add():
    return redirect(url_for("schedule.show"))