"""
Tests for the data transformers.
"""

import pytest
from datetime import date
from decimal import Decimal

from travel_connector.transformers.ratehawk_transformer import RatehawkTransformer
from travel_connector.models.hotel import Hotel, HotelAmenity
from travel_connector.models.room import Room, RoomRate
from travel_connector.models.booking import Booking, BookingStatus
from travel_connector.utils.exceptions import TransformationError


class TestRatehawkTransformer:
    """Test suite for the Ratehawk transformer"""
    
    def setup_method(self):
        """Set up test transformer"""
        self.transformer = RatehawkTransformer()
    
    def test_transform_hotel_data(self):
        """Test transforming hotel data from Ratehawk API"""
        # Sample Ratehawk API response for a hotel
        hotel_data = {
            "id": "123",
            "name": "Test Hotel",
            "description": "A test hotel",
            "star_rating": 4,
            "location": {
                "address": "123 Main St",
                "city": {"name": "Test City"},
                "country": {"name": "Test Country", "code": "TC"},
                "geo": {"lat": 40.7128, "lon": -74.0060}
            },
            "amenities": ["wifi", "pool", "restaurant"]
        }
        
        # Transform the data
        hotel = self.transformer.transform_hotel_data(hotel_data)
        
        # Assertions
        assert isinstance(hotel, Hotel)
        assert hotel.source_id == "123"
        assert hotel.name == "Test Hotel"
        assert hotel.description == "A test hotel"
        assert hotel.category == 4
        assert hotel.location.address.city == "Test City"
        assert hotel.location.address.country == "Test Country"
        assert hotel.location.address.country_code == "TC"
        assert hotel.location.coordinates.latitude == 40.7128
        assert hotel.location.coordinates.longitude == -74.0060
        assert HotelAmenity.WIFI in hotel.amenities
        assert HotelAmenity.POOL in hotel.amenities
        assert HotelAmenity.RESTAURANT in hotel.amenities
    
    def test_transform_hotel_data_missing_id(self):
        """Test error handling when hotel ID is missing"""
        # Sample data with missing ID
        hotel_data = {
            "name": "Test Hotel",
            "location": {
                "address": "123 Main St",
                "city": {"name": "Test City"},
                "country": {"name": "Test Country", "code": "TC"}
            }
        }
        
        # Transform the data and check for error
        with pytest.raises(TransformationError):
            self.transformer.transform_hotel_data(hotel_data)
    
    def test_transform_room_data(self):
        """Test transforming room data from Ratehawk API"""
        # Sample Ratehawk API response for a room
        room_data = {
            "id": "room123",
            "name": "Deluxe Room",
            "description": "A deluxe room",
            "max_occupancy": 2,
            "max_adults": 2,
            "max_children": 0,
            "size_sqm": 30,
            "bed_type": "King",
            "bed_count": 1,
            "amenities": ["wifi", "tv", "mini_bar"],
            "rates": [
                {
                    "id": "rate123",
                    "name": "Standard Rate",
                    "price_per_night": 100.00,
                    "total_price": 300.00,
                    "currency": "USD",
                    "checkin": "2023-06-01",
                    "checkout": "2023-06-04",
                    "max_occupancy": 2,
                    "board_type": "Breakfast included",
                    "is_refundable": True
                }
            ]
        }
        
        # Transform the data
        room = self.transformer.transform_room_data(room_data, hotel_id="hotel123")
        
        # Assertions
        assert isinstance(room, Room)
        assert room.source_id == "room123"
        assert room.hotel_id == "hotel123"
        assert room.name == "Deluxe Room"
        assert room.description == "A deluxe room"
        assert room.max_occupancy == 2
        assert room.max_adults == 2
        assert room.max_children == 0
        assert room.size_sqm == 30
        assert room.bed_type == "King"
        assert room.bed_count == 1
        
        # Check rates
        assert len(room.rates) == 1
        assert isinstance(room.rates[0], RoomRate)
        assert room.rates[0].rate_plan_name == "Standard Rate"
        assert room.rates[0].price_per_night == Decimal("100.00")
        assert room.rates[0].total_price == Decimal("300.00")
        assert room.rates[0].currency == "USD"
        assert room.rates[0].check_in_date == date(2023, 6, 1)
        assert room.rates[0].check_out_date == date(2023, 6, 4)
        assert room.rates[0].is_refundable is True
    
    def test_transform_booking_response(self):
        """Test transforming booking data from Ratehawk API"""
        # Sample Ratehawk API response for a booking
        booking_data = {
            "id": "booking123",
            "reference_number": "TEST123",
            "status": "confirmed",
            "hotel_id": "hotel123",
            "room_id": "room123",
            "rate_id": "rate123",
            "guest": {
                "name": "John Doe",
                "email": "john@example.com",
                "phone": "+1234567890"
            },
            "guests": 2,
            "adults": 2,
            "children": 0,
            "checkin": "2023-06-01",
            "checkout": "2023-06-04",
            "special_requests": "Late check-in",
            "total_price": 300.00,
            "currency": "USD",
            "payment_status": "paid",
            "payment_method": "credit_card",
            "created_at": "2023-05-15T10:30:00Z"
        }
        
        # Transform the data
        booking = self.transformer.transform_booking_response(booking_data)
        
        # Assertions
        assert isinstance(booking, Booking)
        assert booking.source_id == "booking123"
        assert booking.booking_number == "TEST123"
        assert booking.status == BookingStatus.CONFIRMED
        assert booking.hotel_id == "hotel123"
        assert booking.room_id == "room123"
        assert booking.guest_name == "John Doe"
        assert booking.guest_email == "john@example.com"
        assert booking.guest_phone == "+1234567890"
        assert booking.number_of_guests == 2
        assert booking.number_of_adults == 2
        assert booking.number_of_children == 0
        assert booking.check_in_date == date(2023, 6, 1)
        assert booking.check_out_date == date(2023, 6, 4)
        assert booking.special_requests == "Late check-in"
        assert booking.total_price == Decimal("300.00")
        assert booking.currency == "USD"
        assert booking.payment_status == "paid"
        assert booking.payment_method == "credit_card"
    
    def test_transform_search_params(self):
        """Test transforming search parameters to Ratehawk format"""
        # Sample standardized search parameters
        search_params = {
            "location": {
                "city_id": "city123"
            },
            "checkin": "2023-06-01",
            "checkout": "2023-06-04",
            "adults": 2,
            "children": [7, 9],
            "currency": "EUR",
            "language": "en",
            "star_rating": [4, 5],
            "price_range": {
                "min": 50,
                "max": 300
            },
            "amenities": ["wifi", "pool"]
        }
        
        # Transform the parameters
        ratehawk_params = self.transformer.transform_search_params(search_params)
        
        # Assertions
        assert ratehawk_params["city_id"] == "city123"
        assert ratehawk_params["checkin"] == "2023-06-01"
        assert ratehawk_params["checkout"] == "2023-06-04"
        assert ratehawk_params["adults"] == 2
        assert ratehawk_params["children"] == [7, 9]
        assert ratehawk_params["currency"] == "EUR"
        assert ratehawk_params["language"] == "en"
        assert ratehawk_params["star_rating"] == [4, 5]
        assert ratehawk_params["price_min"] == 50
        assert ratehawk_params["price_max"] == 300
        assert ratehawk_params["amenities"] == ["wifi", "pool"]
    
    def test_transform_room_search_params(self):
        """Test transforming room search parameters to Ratehawk format"""
        # Sample standardized room search parameters
        search_params = {
            "checkin": "2023-06-01",
            "checkout": "2023-06-04",
            "adults": 2,
            "children": [7],
            "currency": "EUR"
        }
        
        # Transform the parameters
        ratehawk_params = self.transformer.transform_room_search_params(search_params)
        
        # Assertions
        assert ratehawk_params["checkin"] == "2023-06-01"
        assert ratehawk_params["checkout"] == "2023-06-04"
        assert ratehawk_params["adults"] == 2
        assert ratehawk_params["children"] == [7]
        assert ratehawk_params["currency"] == "EUR"
