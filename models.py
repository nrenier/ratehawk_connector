"""
Database models for the application.
"""

from app import db
from flask_login import UserMixin


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # ensure password hash field has length of at least 256
    password_hash = db.Column(db.String(256))


class SavedHotel(db.Model):
    """Model for storing user favorite/saved hotels"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    source = db.Column(db.String(64), nullable=False, comment="Source API")
    hotel_id = db.Column(db.String(256), nullable=False, comment="Hotel ID from source")
    saved_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    
    # Define a unique constraint to prevent duplicates
    __table_args__ = (db.UniqueConstraint('user_id', 'source', 'hotel_id', name='_user_source_hotel_uc'),)


class BookingRecord(db.Model):
    """Model for storing booking records"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    source = db.Column(db.String(64), nullable=False, comment="Source API")
    booking_id = db.Column(db.String(256), nullable=False, comment="Booking ID from source")
    hotel_id = db.Column(db.String(256), nullable=False, comment="Hotel ID from source")
    room_id = db.Column(db.String(256), nullable=False, comment="Room ID from source")
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    guest_name = db.Column(db.String(256), nullable=False)
    total_price = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    status = db.Column(db.String(64), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now(), onupdate=db.func.now())
    
    # Define a unique constraint for the booking
    __table_args__ = (db.UniqueConstraint('source', 'booking_id', name='_source_booking_uc'),)


class SearchHistory(db.Model):
    """Model for storing user search history"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    location = db.Column(db.String(256), nullable=False)
    check_in_date = db.Column(db.Date, nullable=False)
    check_out_date = db.Column(db.Date, nullable=False)
    adults = db.Column(db.Integer, nullable=False)
    children = db.Column(db.Integer, nullable=False, default=0)
    search_params = db.Column(db.JSON, nullable=True, comment="Additional search parameters")
    searched_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
