from flask import Blueprint, flash, g, redirect, render_template, session, url_for

from app.forms import LoginForm, RegisterForm
from app.services import auth_service
from app.services.auth_service import AuthError

bp = Blueprint("auth", __name__)


@bp.before_app_request
def load_logged_in_user():
    g.user = auth_service.get_user(session.get("user_id"))


@bp.app_context_processor
def inject_user():
    return {"user": g.get("user")}


def flash_errors(form):
    for errors in form.errors.values():
        for error in errors:
            flash(error, "danger")


def log_in(user):
    session.clear()  # nowa sesja po zalogowaniu
    session["user_id"] = user.id


@bp.route("/login", methods=["GET", "POST"])
def login():
    if g.user:
        return redirect(url_for("main.index"))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            log_in(auth_service.authenticate(form.email.data, form.password.data))
            return redirect(url_for("main.index"))
        except AuthError as e:
            flash(str(e), "danger")
    flash_errors(form)
    return render_template("login.html", form=form)


@bp.route("/rejestracja", methods=["GET", "POST"])
def register():
    if g.user:
        return redirect(url_for("main.index"))
    form = RegisterForm()
    if form.validate_on_submit():
        try:
            user = auth_service.register(form.name.data, form.email.data, form.password.data)
            log_in(user)
            flash("Konto utworzone. Witaj w TripForge!", "success")
            return redirect(url_for("main.index"))
        except AuthError as e:
            flash(str(e), "danger")
    flash_errors(form)
    return render_template("register.html", form=form)


@bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
