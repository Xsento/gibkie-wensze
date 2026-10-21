from flask import Blueprint, redirect, render_template, request, url_for

bp = Blueprint("auth", __name__)


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        return redirect(url_for("main.index"))
    return render_template("login.html")


@bp.route("/logout")
def logout():
    return redirect(url_for("auth.login"))