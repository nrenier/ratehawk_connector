"""
Standardized room model representing accommodation unit data
"""

from typing import List, Dict, Optional, Any
from enum import Enum
from decimal import Decimal
from datetime import date
from pydantic import Field, validator

from travel_connector.models.base import BaseModel


class RoomAmenity(str, Enum):
    """Standard room amenities enumeration"""
    AIR_CONDITIONING = "air_conditioning"
    TV = "tv"
    WIFI = "wifi"
    MINI_BAR = "mini_bar"
    SAFE = "safe"
    HAIRDRYER = "hairdryer"
    BATHTUB = "bathtub"
    SHOWER = "shower"
    BALCONY = "balcony"
    KITCHEN = "kitchen"
    COFFEE_MACHINE = "coffee_machine"
    IRON = "iron"
    DESK = "desk"
    TELEPHONE = "telephone"
    BATH_ROBES = "bath_robes"
    SEA_VIEW = "sea_view"
    MOUNTAIN_VIEW = "mountain_view"
    CITY_VIEW = "city_view"
    OTHER = "other"


class RoomRate(BaseModel):
    """Room rate model representing pricing for a specific time period"""
    
    rate_plan_id: str = Field(..., description="Rate plan identifier")
    rate_plan_name: Optional[str] = Field(None, description="Rate plan name")
    
    # Pricing
    price_per_night: Decimal = Field(..., description="Price per night")
    total_price: Decimal = Field(..., description="Total price for the stay")
    currency: str = Field(..., description="Currency code (ISO 4217)")
    
    # Dates
    check_in_date: date = Field(..., description="Check-in date")
    check_out_date: date = Field(..., description="Check-out date")
    
    # Booking details
    max_occupancy: int = Field(..., description="Maximum number of guests")
    board_type: Optional[str] = Field(None, description="Board type (e.g., Breakfast included)")
    
    # Policies
    is_refundable: bool = Field(False, description="Whether the rate is refundable")
    cancellation_policy: Optional[str] = Field(None, description="Cancellation policy description")
    payment_policy: Optional[str] = Field(None, description="Payment policy description")

    @validator('total_price', 'price_per_night')
    def validate_price(cls, v):
        """Validate price is positive"""
        if v <= 0:
            raise ValueError('Price must be greater than zero')
        return v


class Room(BaseModel):
    """Standardized room model"""
    
    hotel_id: str = Field(..., description="ID of the hotel this room belongs to")
    name: str = Field(..., description="Room name/type")
    description: Optional[str] = Field(None, description="Room description")
    
    # Room details
    max_occupancy: int = Field(..., description="Maximum number of guests")
    max_adults: int = Field(..., description="Maximum number of adults")
    max_children: Optional[int] = Field(None, description="Maximum number of children")
    size_sqm: Optional[float] = Field(None, description="Room size in square meters")
    
    # Beds information
    bed_type: Optional[str] = Field(None, description="Type of bed (e.g., King, Twin)")
    bed_count: Optional[int] = Field(None, description="Number of beds")
    
    # Features and amenities
    amenities: List[RoomAmenity] = Field(default_factory=list, description="Room amenities")
    images: List[str] = Field(default_factory=list, description="URLs to room images")
    
    # Additional arbitrary properties
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional room properties")
    
    # Current availability and rates
    available: Optional[bool] = Field(None, description="Whether the room is currently available")
    rates: List[RoomRate] = Field(default_factory=list, description="Available rate plans")

    @validator('max_occupancy', 'max_adults')
    def validate_occupancy(cls, v):
        """Validate occupancy is positive"""
        if v <= 0:
            raise ValueError('Occupancy must be greater than zero')
        return v
