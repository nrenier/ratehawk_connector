"""
Tests for the standardized data models.
"""

import pytest
from datetime import datetime, date, time
from decimal import Decimal

from travel_connector.models.hotel import Hotel, HotelAmenity
from travel_connector.models.room import Room, RoomAmenity, RoomRate
from travel_connector.models.booking import Booking, BookingStatus
from travel_connector.models.location import Location, Address, Coordinates


class TestHotelModel:
    """Test suite for the Hotel model"""
    
    def test_hotel_creation(self):
        """Test creating a valid Hotel instance"""
        # Create test data
        address = Address(
            line1="123 Main St",
            city="Test City",
            country="Test Country",
            country_code="TC",
            source="test",
            source_id="test_address_1",
            id="test_address_1"
        )
        
        coordinates = Coordinates(
            latitude=40.7128,
            longitude=-74.0060,
            source="test",
            source_id="test_coords_1",
            id="test_coords_1"
        )
        
        location = Location(
            address=address,
            coordinates=coordinates,
            source="test",
            source_id="test_location_1",
            id="test_location_1"
        )
        
        # Create hotel
        hotel = Hotel(
            id="test_hotel_1",
            source="test",
            source_id="1",
            name="Test Hotel",
            description="A test hotel",
            category=4,
            location=location,
            amenities=[HotelAmenity.WIFI, HotelAmenity.POOL]
        )
        
        # Assertions
        assert hotel.id == "test_hotel_1"
        assert hotel.source == "test"
        assert hotel.source_id == "1"
        assert hotel.name == "Test Hotel"
        assert hotel.description == "A test hotel"
        assert hotel.category == 4
        assert hotel.location.address.city == "Test City"
        assert hotel.location.coordinates.latitude == 40.7128
        assert HotelAmenity.WIFI in hotel.amenities
        assert HotelAmenity.POOL in hotel.amenities
    
    def test_hotel_validation(self):
        """Test hotel validation rules"""
        address = Address(
            line1="123 Main St",
            city="Test City",
            country="Test Country",
            country_code="TC",
            source="test",
            source_id="test_address_1",
            id="test_address_1"
        )
        
        location = Location(
            address=address,
            source="test",
            source_id="test_location_1",
            id="test_location_1"
        )
        
        # Test invalid star rating
        with pytest.raises(ValueError):
            Hotel(
                id="test_hotel_1",
                source="test",
                source_id="1",
                name="Test Hotel",
                category=6,  # Invalid: must be 1-5
                location=location
            )
        
        # Test invalid rating
        with pytest.raises(ValueError):
            Hotel(
                id="test_hotel_1",
                source="test",
                source_id="1",
                name="Test Hotel",
                location=location,
                rating=11  # Invalid: must be 0-10
            )


class TestRoomModel:
    """Test suite for the Room model"""
    
    def test_room_creation(self):
        """Test creating a valid Room instance"""
        # Create room rate
        rate = RoomRate(
            id="test_rate_1",
            source="test",
            source_id="rate1",
            rate_plan_id="rate1",
            rate_plan_name="Standard Rate",
            price_per_night=Decimal("100.00"),
            total_price=Decimal("300.00"),
            currency="USD",
            check_in_date=date(2023, 6, 1),
            check_out_date=date(2023, 6, 4),
            max_occupancy=2
        )
        
        # Create room
        room = Room(
            id="test_room_1",
            source="test",
            source_id="room1",
            hotel_id="test_hotel_1",
            name="Deluxe Room",
            max_occupancy=2,
            max_adults=2,
            amenities=[RoomAmenity.WIFI, RoomAmenity.TV],
            rates=[rate]
        )
        
        # Assertions
        assert room.id == "test_room_1"
        assert room.source == "test"
        assert room.source_id == "room1"
        assert room.hotel_id == "test_hotel_1"
        assert room.name == "Deluxe Room"
        assert room.max_occupancy == 2
        assert room.max_adults == 2
        assert RoomAmenity.WIFI in room.amenities
        assert RoomAmenity.TV in room.amenities
        assert len(room.rates) == 1
        assert room.rates[0].price_per_night == Decimal("100.00")
    
    def test_room_validation(self):
        """Test room validation rules"""
        # Test invalid occupancy
        with pytest.raises(ValueError):
            Room(
                id="test_room_1",
                source="test",
                source_id="room1",
                hotel_id="test_hotel_1",
                name="Deluxe Room",
                max_occupancy=0,  # Invalid: must be > 0
                max_adults=2
            )
        
        # Test invalid adults
        with pytest.raises(ValueError):
            Room(
                id="test_room_1",
                source="test",
                source_id="room1",
                hotel_id="test_hotel_1",
                name="Deluxe Room",
                max_occupancy=2,
                max_adults=0  # Invalid: must be > 0
            )


class TestBookingModel:
    """Test suite for the Booking model"""
    
    def test_booking_creation(self):
        """Test creating a valid Booking instance"""
        # Create booking
        booking = Booking(
            id="test_booking_1",
            source="test",
            source_id="booking1",
            booking_number="TEST123",
            status=BookingStatus.CONFIRMED,
            hotel_id="test_hotel_1",
            room_id="test_room_1",
            guest_name="John Doe",
            number_of_guests=2,
            number_of_adults=2,
            check_in_date=date(2023, 6, 1),
            check_out_date=date(2023, 6, 4),
            total_price=Decimal("300.00"),
            currency="USD",
            booked_at=datetime(2023, 5, 15, 10, 30)
        )
        
        # Assertions
        assert booking.id == "test_booking_1"
        assert booking.source == "test"
        assert booking.source_id == "booking1"
        assert booking.booking_number == "TEST123"
        assert booking.status == BookingStatus.CONFIRMED
        assert booking.hotel_id == "test_hotel_1"
        assert booking.room_id == "test_room_1"
        assert booking.guest_name == "John Doe"
        assert booking.number_of_guests == 2
        assert booking.check_in_date == date(2023, 6, 1)
        assert booking.check_out_date == date(2023, 6, 4)
        assert booking.total_price == Decimal("300.00")
        assert booking.currency == "USD"
    
    def test_booking_date_validation(self):
        """Test booking date validation rules"""
        # Test invalid date range
        with pytest.raises(ValueError):
            Booking(
                id="test_booking_1",
                source="test",
                source_id="booking1",
                booking_number="TEST123",
                status=BookingStatus.CONFIRMED,
                hotel_id="test_hotel_1",
                room_id="test_room_1",
                guest_name="John Doe",
                number_of_guests=2,
                number_of_adults=2,
                check_in_date=date(2023, 6, 4),  # Invalid: checkout must be after checkin
                check_out_date=date(2023, 6, 1),
                total_price=Decimal("300.00"),
                currency="USD",
                booked_at=datetime(2023, 5, 15, 10, 30)
            )
