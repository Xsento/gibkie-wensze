from sqlalchemy import func

from app.extensions import db
from app.models import Availability, Trip, TripMember, User


def get_member(member_id):
    return db.session.get(TripMember, member_id)


def get_membership(trip_id, user_id):
    return TripMember.query.filter_by(trip_id=trip_id, user_id=user_id).first()


def trips_of_user(user_id):
    return (Trip.query.join(TripMember)
            .filter(TripMember.user_id == user_id)
            .order_by(Trip.start_date, Trip.id)
            .all())


def get_availability(member_id, day):
    return Availability.query.filter_by(trip_member_id=member_id, day=day).first()


def save(obj):
    db.session.add(obj)
    db.session.commit()
    return obj


def rollback():
    db.session.rollback()


def count_available_by_day(trip_id):
    rows = (db.session.query(Availability.day, func.count(Availability.id))
            .join(TripMember)
            .filter(TripMember.trip_id == trip_id, Availability.state.is_(True))
            .group_by(Availability.day)
            .all())
    return dict(rows)


def available_names_by_day(trip_id):
    rows = (db.session.query(Availability.day, TripMember.name)
            .join(TripMember)
            .filter(TripMember.trip_id == trip_id, Availability.state.is_(True))
            .order_by(Availability.day, TripMember.name)
            .all())
    names = {}
    for day, name in rows:
        names.setdefault(day, []).append(name)
    return names


def available_days_of_member(member_id):
    rows = Availability.query.filter_by(trip_member_id=member_id, state=True).all()
    return {a.day for a in rows}


def count_members(trip_id):
    return TripMember.query.filter_by(trip_id=trip_id).count()


def add_trip(title, start_date, end_date, organizer, member_users):
    members = [TripMember(user_id=organizer.id, name=organizer.name, is_organizer=True)]
    members += [TripMember(user_id=user.id, name=user.name) for user in member_users]
    trip = Trip(title=title, start_date=start_date, end_date=end_date, members=members)
    return save(trip)
