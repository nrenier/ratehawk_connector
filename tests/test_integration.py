"""
Integration tests for the travel connector.

These tests evaluate the end-to-end functionality of the connector
with real-world scenarios. They require actual API credentials to run.
"""

import os
import pytest
import logging
from datetime import date, timedelta
from decimal import Decimal

from travel_connector.main import create_connector
from travel_connector.config import get_api_key
from travel_connector.models.hotel import Hotel
from travel_connector.models.room import Room
from travel_connector.models.booking import Booking, BookingStatus
from travel_connector.utils.exceptions import ConnectorError

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class TestConnectorIntegration:
    """Integration test suite for the TravelConnector class"""
    
    @pytest.fixture
    def connector(self):
        """Create a connector fixture for tests"""
        try:
            # Skip if no API key is available
            get_api_key("ratehawk")
            return create_connector()
        except (ValueError, ConnectorError) as e:
            pytest.skip(f"Skipping due to missing API credentials: {str(e)}")
    
    @pytest.mark.integration
    def test_hotel_search_flow(self, connector):
        """Test the complete hotel search flow"""
        if not connector:
            pytest.skip("Connector not initialized")
        
        # Define search parameters
        tomorrow = date.today() + timedelta(days=1)
        next_week = tomorrow + timedelta(days=7)
        
        search_params = {
            "location": {
                "city_id": "rome"  # Using a popular city that's likely to have hotels
            },
            "checkin": tomorrow.isoformat(),
            "checkout": next_week.isoformat(),
            "adults": 2,
            "children": [],
            "currency": "EUR"
        }
        
        # 1. Search for hotels
        try:
            hotels = connector.search_hotels("ratehawk", search_params)
            assert hotels, "No hotels found"
            assert len(hotels) > 0, "No hotels found in search results"
            assert all(isinstance(hotel, Hotel) for hotel in hotels), "Invalid hotel objects in results"
            
            # Verify hotel structure
            hotel = hotels[0]
            assert hotel.id is not None
            assert hotel.name is not None
            assert hotel.location is not None
            assert hotel.location.address is not None
            assert hotel.location.address.city is not None
            
            logger.info(f"Found {len(hotels)} hotels in {search_params['location'].get('city_id')}")
            
            # 2. Get detailed info for the first hotel
            hotel_id = hotel.id
            detailed_hotel = connector.get_hotel_details("ratehawk", hotel_id)
            assert detailed_hotel is not None, "Failed to get hotel details"
            assert detailed_hotel.id == hotel_id, "Hotel ID mismatch"
            assert detailed_hotel.description is not None, "Missing hotel description"
            
            # 3. Search for rooms in the hotel
            rooms = connector.search_rooms("ratehawk", hotel_id, search_params)
            assert rooms is not None, "No rooms found"
            if len(rooms) > 0:
                assert all(isinstance(room, Room) for room in rooms), "Invalid room objects in results"
                
                # Verify room structure
                room = rooms[0]
                assert room.id is not None
                assert room.name is not None
                assert room.hotel_id is not None
                assert room.max_occupancy > 0
                
                if room.rates and len(room.rates) > 0:
                    rate = room.rates[0]
                    assert rate.price_per_night > Decimal('0')
                    assert rate.total_price > Decimal('0')
                    assert rate.currency is not None
            else:
                logger.warning("No available rooms found for the selected hotel")
                
        except ConnectorError as e:
            logger.error(f"API error: {str(e)}")
            pytest.fail(f"API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            pytest.fail(f"Unexpected error: {str(e)}")
    
    @pytest.mark.integration
    def test_booking_flow(self, connector, monkeypatch):
        """Test the booking creation and management flow"""
        if not connector:
            pytest.skip("Connector not initialized")
            
        # Mock the create_booking method to avoid actual bookings
        def mock_create_booking(self, booking_data):
            """Mock booking creation"""
            from travel_connector.models.booking import Booking, BookingStatus
            from datetime import datetime
            
            # Create a mock booking object
            return Booking(
                id="ratehawk_booking_mock123",
                source="ratehawk",
                source_id="mock123",
                booking_number="MOCK123",
                status=BookingStatus.CONFIRMED,
                hotel_id=booking_data.get("hotel_id"),
                room_id=booking_data.get("room_id"),
                rate_plan_id=booking_data.get("rate_id"),
                guest_name="John Doe",
                guest_email="john@example.com",
                guest_phone="+1234567890",
                number_of_guests=booking_data.get("adults", 2),
                number_of_adults=booking_data.get("adults", 2),
                number_of_children=0,
                check_in_date=datetime.strptime(booking_data.get("checkin"), "%Y-%m-%d").date() if isinstance(booking_data.get("checkin"), str) else booking_data.get("checkin"),
                check_out_date=datetime.strptime(booking_data.get("checkout"), "%Y-%m-%d").date() if isinstance(booking_data.get("checkout"), str) else booking_data.get("checkout"),
                special_requests=booking_data.get("special_requests"),
                total_price=Decimal("100.00"),
                currency="EUR",
                payment_status="pending",
                payment_method="credit_card",
                booked_at=datetime.utcnow(),
                cancelled_at=None
            )
        
        # Mock the get_booking and cancel_booking methods
        def mock_get_booking(self, booking_id):
            """Mock get booking details"""
            from travel_connector.models.booking import Booking, BookingStatus
            from datetime import datetime, date
            
            return Booking(
                id=booking_id,
                source="ratehawk",
                source_id=booking_id.replace("ratehawk_booking_", ""),
                booking_number="MOCK123",
                status=BookingStatus.CONFIRMED,
                hotel_id="hotel123",
                room_id="room123",
                rate_plan_id="rate123",
                guest_name="John Doe",
                guest_email="john@example.com",
                guest_phone="+1234567890",
                number_of_guests=2,
                number_of_adults=2,
                number_of_children=0,
                check_in_date=date.today() + timedelta(days=1),
                check_out_date=date.today() + timedelta(days=8),
                special_requests=None,
                total_price=Decimal("100.00"),
                currency="EUR",
                payment_status="pending",
                payment_method="credit_card",
                booked_at=datetime.utcnow(),
                cancelled_at=None
            )
        
        def mock_cancel_booking(self, booking_id):
            """Mock cancel booking"""
            booking = mock_get_booking(self, booking_id)
            booking.status = BookingStatus.CANCELLED
            booking.cancelled_at = datetime.utcnow()
            return booking
        
        # Apply the mocks
        from travel_connector.adapters.ratehawk_adapter import RatehawkAdapter
        monkeypatch.setattr(RatehawkAdapter, "create_booking", mock_create_booking)
        monkeypatch.setattr(RatehawkAdapter, "get_booking", mock_get_booking)
        monkeypatch.setattr(RatehawkAdapter, "cancel_booking", mock_cancel_booking)
        
        # Define booking data
        tomorrow = date.today() + timedelta(days=1)
        next_week = tomorrow + timedelta(days=7)
        
        booking_data = {
            "hotel_id": "ratehawk_hotel_123",
            "room_id": "ratehawk_room_456",
            "rate_id": "ratehawk_rate_789",
            "checkin": tomorrow.isoformat(),
            "checkout": next_week.isoformat(),
            "guest": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john@example.com",
                "phone": "+1234567890"
            },
            "adults": 2,
            "children": [],
            "special_requests": "Late check-in",
            "currency": "EUR"
        }
        
        try:
            # 1. Create a booking
            booking = connector.create_booking("ratehawk", booking_data)
            assert booking is not None, "Failed to create booking"
            assert isinstance(booking, Booking), "Invalid booking object"
            assert booking.status == BookingStatus.CONFIRMED, "Booking not confirmed"
            assert booking.id is not None, "Booking ID is missing"
            
            booking_id = booking.id
            logger.info(f"Created booking with ID: {booking_id}")
            
            # 2. Retrieve the booking
            retrieved_booking = connector.get_booking("ratehawk", booking_id)
            assert retrieved_booking is not None, "Failed to retrieve booking"
            assert retrieved_booking.id == booking_id, "Booking ID mismatch"
            assert retrieved_booking.status == BookingStatus.CONFIRMED, "Booking status mismatch"
            
            # 3. Cancel the booking
            cancelled_booking = connector.cancel_booking("ratehawk", booking_id)
            assert cancelled_booking is not None, "Failed to cancel booking"
            assert cancelled_booking.id == booking_id, "Booking ID mismatch"
            assert cancelled_booking.status == BookingStatus.CANCELLED, "Booking not cancelled"
            assert cancelled_booking.cancelled_at is not None, "Cancellation timestamp missing"
            
            logger.info(f"Successfully cancelled booking: {booking_id}")
            
        except ConnectorError as e:
            logger.error(f"API error: {str(e)}")
            pytest.fail(f"API error: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            pytest.fail(f"Unexpected error: {str(e)}")
