"""
Standardized booking model representing reservation data
"""

from typing import List, Dict, Optional, Any
from enum import Enum
from decimal import Decimal
from datetime import datetime, date
from pydantic import Field, validator

from travel_connector.models.base import BaseModel


class BookingStatus(str, Enum):
    """Booking status enumeration"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    FAILED = "failed"


class Booking(BaseModel):
    """Standardized booking model"""
    
    # Booking details
    booking_number: str = Field(..., description="Booking reference number")
    status: BookingStatus = Field(..., description="Current booking status")
    
    # Related entities
    hotel_id: str = Field(..., description="ID of the booked hotel")
    room_id: str = Field(..., description="ID of the booked room")
    rate_plan_id: Optional[str] = Field(None, description="ID of the selected rate plan")
    
    # Customer details
    guest_name: str = Field(..., description="Main guest name")
    guest_email: Optional[str] = Field(None, description="Guest email address")
    guest_phone: Optional[str] = Field(None, description="Guest phone number")
    number_of_guests: int = Field(..., description="Total number of guests")
    number_of_adults: int = Field(..., description="Number of adults")
    number_of_children: int = Field(0, description="Number of children")
    
    # Stay details
    check_in_date: date = Field(..., description="Check-in date")
    check_out_date: date = Field(..., description="Check-out date")
    special_requests: Optional[str] = Field(None, description="Special requests or notes")
    
    # Payment details
    total_price: Decimal = Field(..., description="Total booking price")
    currency: str = Field(..., description="Currency code (ISO 4217)")
    payment_status: Optional[str] = Field(None, description="Status of payment")
    payment_method: Optional[str] = Field(None, description="Method of payment")
    
    # Timestamps
    booked_at: datetime = Field(..., description="When the booking was made")
    cancelled_at: Optional[datetime] = Field(None, description="When the booking was cancelled")
    
    # Additional arbitrary properties
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional booking properties")

    @validator('check_out_date')
    def validate_dates(cls, v, values):
        """Validate check-out date is after check-in date"""
        if 'check_in_date' in values and v <= values['check_in_date']:
            raise ValueError('Check-out date must be after check-in date')
        return v
