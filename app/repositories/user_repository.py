from app.extensions import db
from app.models import TripMember, User


def get_user(user_id):
    return db.session.get(User, user_id)


def get_by_email(email):
    return User.query.filter_by(email=email).first()


def first_membership(user_id):
    return TripMember.query.filter_by(user_id=user_id).order_by(TripMember.id).first()


def save(obj):
    db.session.add(obj)
    db.session.commit()
    return obj


def rollback():
    db.session.rollback()
