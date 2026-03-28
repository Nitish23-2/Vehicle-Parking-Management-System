from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
from zoneinfo import ZoneInfo
import pytz

from . import db

class User(UserMixin, db.Model):
    id=db.Column(db.Integer, primary_key=True)
    full_name=db.Column(db.String(100), nullable=False)
    email= db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)

    reservations=db.relationship('Reservation', backref='user', lazy=True)

    def __repr__(self):
        return f'<user{self.email}>'
    
class ParkingLot(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    location_name= db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(200), nullable=False)
    pincode= db.Column(db.String(10), nullable=False)
    price_per_hour= db.Column(db.Float, nullable=False)
    max_spots= db.Column(db.Integer, nullable=False)

    spots= db.relationship('ParkingSpot', backref='lot', lazy=True)
    
    def __repr__(self):
        return f'<ParkingLot {self.location_name}'

class ParkingSpot(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    lot_id= db.Column(db.Integer, db.ForeignKey('parking_lot.id'), nullable=False)
    status= db.Column(db.String(1), default="A") # A for available and O for Occupied

    reservations= db.relationship("Reservation", backref='spot', lazy=True)

    def current_reservation(self):
        return next((res for res in self.reservations if res.end_time is None),None)

    def __repr__(self): 
        return f'<Spot {self.id} in Lot {self.lot_id}>'

IST= ZoneInfo('Asia/Kolkata')
class Reservation(db.Model):
    id= db.Column(db.Integer, primary_key=True)
    spot_id= db.Column(db.Integer, db.ForeignKey('parking_spot.id'), nullable=False)
    user_id= db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_number= db.Column(db.String(20), nullable=False)
    start_time= db.Column(db.DateTime, default=datetime.now(IST))
    end_time= db.Column(db.DateTime, nullable=True)
    cost= db.Column(db.Float, default=0.0)

    def __repr__(self):
        return f'<Reservation {self.id} -Spot {self.spot_id} -User {self.user_id}>'
    