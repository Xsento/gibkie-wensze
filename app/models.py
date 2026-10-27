from sqlalchemy import UniqueConstraint
from app.extensions import db


class Trip(db.Model):
    __tablename__ = 'trips'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120), nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    approved_start = db.Column(db.Date)
    approved_end = db.Column(db.Date)

    members = db.relationship('TripMember', backref='trip', lazy=True, cascade='all, delete-orphan')


class TripMember(db.Model):
    __tablename__ = 'trip_members'

    id = db.Column(db.Integer, primary_key=True)
    trip_id = db.Column(db.Integer, db.ForeignKey('trips.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(80), nullable=False)
    is_organizer = db.Column(db.Boolean, nullable=False, default=False)

    availabilities = db.relationship('Availability', backref='member', lazy=True, cascade='all, delete-orphan')


class Availability(db.Model):
    __tablename__ = 'availabilities'

    id = db.Column(db.Integer, primary_key=True)
    trip_member_id = db.Column(db.Integer, db.ForeignKey('trip_members.id', ondelete='CASCADE'), nullable=False)
    day = db.Column(db.Date, nullable=False)
    
    state = db.Column(db.Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint('trip_member_id', 'day', name='uq_member_day'),
    )
