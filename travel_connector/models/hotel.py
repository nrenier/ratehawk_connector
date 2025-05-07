"""
Standardized hotel model representing accommodation data
"""

from typing import List, Dict, Optional, Any
from enum import Enum
from datetime import datetime, time
from pydantic import Field, validator

from travel_connector.models.base import BaseModel
from travel_connector.models.location import Location


class HotelAmenity(str, Enum):
    """Standard hotel amenities enumeration"""
    WIFI = "wifi"
    POOL = "pool"
    FITNESS_CENTER = "fitness_center"
    RESTAURANT = "restaurant"
    BAR = "bar"
    SPA = "spa"
    ROOM_SERVICE = "room_service"
    PARKING = "parking"
    BUSINESS_CENTER = "business_center"
    BREAKFAST = "breakfast"
    LAUNDRY = "laundry"
    SHUTTLE = "shuttle"
    CONCIERGE = "concierge"
    AIR_CONDITIONING = "air_conditioning"
    DISABLED_ACCESS = "disabled_access"
    PET_FRIENDLY = "pet_friendly"
    BEACH_ACCESS = "beach_access"
    SKI_ACCESS = "ski_access"
    OTHER = "other"


class Hotel(BaseModel):
    """Standardized hotel model"""
    
    name: str = Field(..., description="Hotel name")
    description: Optional[str] = Field(None, description="Hotel description")
    category: Optional[int] = Field(None, description="Hotel star rating (1-5)")
    location: Location = Field(..., description="Hotel location details")
    
    # Contact information
    phone: Optional[str] = Field(None, description="Hotel contact phone number")
    email: Optional[str] = Field(None, description="Hotel contact email")
    website: Optional[str] = Field(None, description="Hotel website URL")
    
    # Hotel details
    amenities: List[HotelAmenity] = Field(default_factory=list, description="Available hotel amenities")
    images: List[str] = Field(default_factory=list, description="URLs to hotel images")
    check_in_time: Optional[time] = Field(None, description="Standard check-in time")
    check_out_time: Optional[time] = Field(None, description="Standard check-out time")
    
    # Additional arbitrary properties
    properties: Dict[str, Any] = Field(default_factory=dict, description="Additional hotel properties")
    
    # Hotel policies
    cancellation_policy: Optional[str] = Field(None, description="Hotel cancellation policy")
    children_policy: Optional[str] = Field(None, description="Hotel policy for children")
    pet_policy: Optional[str] = Field(None, description="Hotel policy for pets")
    
    # Ratings and reviews
    rating: Optional[float] = Field(None, description="Overall hotel rating (0-10)")
    review_count: Optional[int] = Field(None, description="Number of reviews")
    
    @validator('category')
    def validate_category(cls, v):
        """Validate hotel star rating is between 1 and 5"""
        if v is not None and (v < 1 or v > 5):
            raise ValueError('Hotel category must be between 1 and 5 stars')
        return v
    
    @validator('rating')
    def validate_rating(cls, v):
        """Validate hotel rating is between 0 and 10"""
        if v is not None and (v < 0 or v > 10):
            raise ValueError('Hotel rating must be between 0 and 10')
        return v
