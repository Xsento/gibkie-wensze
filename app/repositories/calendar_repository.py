from sqlalchemy import func

from app.extensions import db
from app.models import Availability, Trip, TripMember


def get_member(member_id):
    return db.session.get(TripMember, member_id)


def get_availability(member_id, day):
    return Availability.query.filter_by(trip_member_id=member_id, day=day).first()


def save(obj):
    db.session.add(obj)
    db.session.commit()
    return obj


def count_available_by_day(trip_id):
    rows = (db.session.query(Availability.day, func.count(Availability.id))
            .join(TripMember)
            .filter(TripMember.trip_id == trip_id, Availability.state.is_(True))
            .group_by(Availability.day)
            .all())
    return dict(rows)


def available_days_of_member(member_id):
    rows = Availability.query.filter_by(trip_member_id=member_id, state=True).all()
    return {a.day for a in rows}


def count_members(trip_id):
    return TripMember.query.filter_by(trip_id=trip_id).count()


def add_trip(title, start_date, end_date, organizer_name, member_names):
    members = [TripMember(name=organizer_name, is_organizer=True)]
    members += [TripMember(name=name) for name in member_names]
    trip = Trip(title=title, start_date=start_date, end_date=end_date, members=members)
    return save(trip)
