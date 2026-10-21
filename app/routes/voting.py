from flask import Blueprint, redirect, render_template, url_for

bp = Blueprint("voting", __name__, url_prefix="/glosowanie")


@bp.route("/")
def show():
    return render_template("voting.html")


@bp.route("/<int:proposal_id>", methods=["POST"])
def vote(proposal_id):
    return redirect(url_for("voting.show"))