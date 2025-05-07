"""
Tests for the API adapters.
"""

import pytest
import responses
from datetime import date, datetime
from decimal import Decimal

from travel_connector.adapters.ratehawk_adapter import RatehawkAdapter
from travel_connector.models.hotel import Hotel
from travel_connector.models.room import Room
from travel_connector.models.booking import Booking, BookingStatus
from travel_connector.utils.exceptions import AdapterError


class TestRatehawkAdapter:
    """Test suite for the Ratehawk adapter"""
    
    def setup_method(self):
        """Set up test adapter"""
        self.adapter = RatehawkAdapter(
            api_key="test_api_key",
            api_url="https://api.test.com"
        )
    
    @responses.activate
    def test_search_hotels(self):
        """Test hotel search functionality"""
        # Mock API response
        responses.add(
            responses.GET,
            "https://api.test.com/hotels/search",
            json={
                "hotels": [
                    {
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
                        "amenities": ["wifi", "pool"]
                    }
                ]
            },
            status=200
        )
        
        # Call the method
        search_params = {
            "location": {"city_id": "city123"},
            "checkin": "2023-06-01",
            "checkout": "2023-06-04",
            "adults": 2
        }
        
        hotels = self.adapter.search_hotels(search_params)
        
        # Assertions
        assert len(hotels) == 1
        assert isinstance(hotels[0], Hotel)
        assert hotels[0].name == "Test Hotel"
        assert hotels[0].category == 4
        assert hotels[0].location.address.city == "Test City"
    
    @responses.activate
    def test_search_hotels_error(self):
        """Test error handling in hotel search"""
        # Mock API error response
        responses.add(
            responses.GET,
            "https://api.test.com/hotels/search",
            json={"error": "Invalid request"},
            status=400
        )
        
        # Call the method and check for error
        search_params = {
            "location": {"city_id": "city123"},
            "checkin": "2023-06-01",
            "checkout": "2023-06-04",
            "adults": 2
        }
        
        with pytest.raises(AdapterError):
            self.adapter.search_hotels(search_params)
    
    @responses.activate
    def test_get_hotel_details(self):
        """Test getting hotel details"""
        # Mock API response
        responses.add(
            responses.GET,
            "https://api.test.com/hotels/123",
            json={
                "id": "123",
                "name": "Test Hotel",
                "description": "A test hotel with details",
                "star_rating": 4,
                "location": {
                    "address": "123 Main St",
                    "city": {"name": "Test City"},
                    "country": {"name": "Test Country", "code": "TC"},
                    "geo": {"lat": 40.7128, "lon": -74.0060}
                },
                "amenities": ["wifi", "pool"],
                "details": {
                    "checkin_time": "14:00",
                    "checkout_time": "12:00",
                    "cancellation_policy": "Free cancellation up to 2 days before arrival"
                },
                "rating": 8.5,
                "review_count": 120
            },
            status=200
        )
        
        # Call the method
        hotel = self.adapter.get_hotel_details("123")
        
        # Assertions
        assert isinstance(hotel, Hotel)
        assert hotel.name == "Test Hotel"
        assert hotel.description == "A test hotel with details"
        assert hotel.rating == 8.5
        assert hotel.review_count == 120
    
    @responses.activate
    def test_search_rooms(self):
        """Test room search functionality"""
        # Mock API response
        responses.add(
            responses.GET,
            "https://api.test.com/hotels/rates",
            json={
                "rooms": [
                    {
                        "id": "room123",
                        "name": "Deluxe Room",
                        "description": "A deluxe room",
                        "max_occupancy": 2,
                        "max_adults": 2,
                        "max_children": 0,
                        "amenities": ["wifi", "tv"],
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
                ]
            },
            status=200
        )
        
        # Call the method
        search_params = {
            "checkin": "2023-06-01",
            "checkout": "2023-06-04",
            "adults": 2
        }
        
        rooms = self.adapter.search_rooms("hotel123", search_params)
        
        # Assertions
        assert len(rooms) == 1
        assert isinstance(rooms[0], Room)
        assert rooms[0].name == "Deluxe Room"
        assert rooms[0].max_occupancy == 2
        assert len(rooms[0].rates) == 1
        assert rooms[0].rates[0].price_per_night == Decimal("100.00")
    
    @responses.activate
    def test_create_booking(self):
        """Test booking creation"""
        # Mock API response
        responses.add(
            responses.POST,
            "https://api.test.com/bookings",
            json={
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
                "total_price": 300.00,
                "currency": "USD",
                "created_at": "2023-05-15T10:30:00Z"
            },
            status=200
        )
        
        # Call the method
        booking_data = {
            "hotel_id": "hotel123",
            "room_id": "room123",
            "rate_id": "rate123",
            "checkin": "2023-06-01",
            "checkout": "2023-06-04",
            "guest": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone": "+1234567890"
            },
            "adults": 2
        }
        
        booking = self.adapter.create_booking(booking_data)
        
        # Assertions
        assert isinstance(booking, Booking)
        assert booking.booking_number == "TEST123"
        assert booking.status == BookingStatus.CONFIRMED
        assert booking.hotel_id == "hotel123"
        assert booking.room_id == "room123"
        assert booking.guest_name == "John Doe"
        assert booking.number_of_adults == 2
        assert booking.total_price == Decimal("300.00")
