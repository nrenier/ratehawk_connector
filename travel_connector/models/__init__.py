"""
Models package containing the standardized data model for travel industry entities.
"""

from travel_connector.models.base import BaseModel
from travel_connector.models.hotel import Hotel, HotelAmenity
from travel_connector.models.room import Room, RoomAmenity, RoomRate
from travel_connector.models.booking import Booking, BookingStatus
from travel_connector.models.location import Location, Address, Coordinates

__all__ = [
    'BaseModel',
    'Hotel',
    'HotelAmenity',
    'Room',
    'RoomAmenity',
    'RoomRate',
    'Booking',
    'BookingStatus',
    'Location',
    'Address',
    'Coordinates'
]
