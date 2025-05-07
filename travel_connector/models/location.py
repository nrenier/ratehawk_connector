"""
Standardized location model representing geographical and address data
"""

from typing import Optional, List
from pydantic import Field, validator

from travel_connector.models.base import BaseModel


class Coordinates(BaseModel):
    """Geographic coordinates model"""
    
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    
    @validator('latitude')
    def validate_latitude(cls, v):
        """Validate latitude is within valid range"""
        if v < -90 or v > 90:
            raise ValueError('Latitude must be between -90 and 90')
        return v
    
    @validator('longitude')
    def validate_longitude(cls, v):
        """Validate longitude is within valid range"""
        if v < -180 or v > 180:
            raise ValueError('Longitude must be between -180 and 180')
        return v


class Address(BaseModel):
    """Physical address model"""
    
    line1: str = Field(..., description="Address line 1")
    line2: Optional[str] = Field(None, description="Address line 2")
    city: str = Field(..., description="City")
    postal_code: Optional[str] = Field(None, description="Postal/ZIP code")
    state: Optional[str] = Field(None, description="State/Province/Region")
    country: str = Field(..., description="Country name")
    country_code: str = Field(..., description="Country code (ISO 3166-1 alpha-2)")
    formatted_address: Optional[str] = Field(None, description="Full formatted address")


class Location(BaseModel):
    """Standardized location model"""
    
    address: Address = Field(..., description="Physical address")
    coordinates: Optional[Coordinates] = Field(None, description="Geographic coordinates")
    
    # Location descriptions
    neighborhood: Optional[str] = Field(None, description="Neighborhood name")
    district: Optional[str] = Field(None, description="District name")
    
    # Points of interest
    nearby_attractions: List[str] = Field(default_factory=list, description="Nearby attractions or landmarks")
    distance_to_center: Optional[float] = Field(None, description="Distance to city center (km)")
    distance_to_airport: Optional[float] = Field(None, description="Distance to nearest airport (km)")
    
    # Other location attributes
    is_beachfront: Optional[bool] = Field(None, description="Whether the location is on the beach")
    is_city_center: Optional[bool] = Field(None, description="Whether the location is in city center")
