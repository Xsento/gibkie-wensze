from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import UniqueConstraint
from app.extensions import db

class TripMember(db.Model):
    __tablename__ = 'trip_members'

    id = db.Column(db.Integer, primary_key=True)

    availabilities = db.relationship('Availability', backref='member', lazy=True, cascade='all, delete-orphan')


class Availability(db.Model):
    __tablename__ = 'availabilities'

    id = db.Column(db.Integer, primary_key=True)
    trip_member_id = db.Column(db.Integer, db.ForeignKey('trip_members.id', ondelete='CASCADE'), nullable=False)
    day = db.Column(db.Date, nullable=False)
    
    state = db.Column(db.Boolean, nullable=False, default=True)

    # only one entry per day from user
    __table_args__ = (
        UniqueConstraint('trip_member_id', 'day', name='uq_member_day'),
    )
