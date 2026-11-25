from sqlalchemy import UniqueConstraint
from app.extensions import db
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    name = db.Column(db.String(80), nullable=False)

    memberships = db.relationship('TripMember', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


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
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)

    availabilities = db.relationship('Availability', backref='member', lazy=True, cascade='all, delete-orphan')

    # jeden użytkownik może być tylko raz uczestnikiem danego wyjazdu,
    # dzięki temu jego dostępność nie jest liczona wielokrotnie
    __table_args__ = (
        UniqueConstraint('trip_id', 'user_id', name='uq_trip_user'),
    )


class Availability(db.Model):
    __tablename__ = 'availabilities'

    id = db.Column(db.Integer, primary_key=True)
    trip_member_id = db.Column(db.Integer, db.ForeignKey('trip_members.id', ondelete='CASCADE'), nullable=False)
    day = db.Column(db.Date, nullable=False)
    
    state = db.Column(db.Boolean, nullable=False, default=True)

    __table_args__ = (
        UniqueConstraint('trip_member_id', 'day', name='uq_member_day'),
    )
