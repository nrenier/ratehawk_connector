"""
Base transformer class that all API-specific transformers will inherit from.
"""

import abc
import logging
from typing import Dict, Any, List, Optional, Type, TypeVar, Generic

from travel_connector.models.base import BaseModel
from travel_connector.models.hotel import Hotel
from travel_connector.models.room import Room
from travel_connector.models.booking import Booking
from travel_connector.utils.exceptions import TransformationError

# Type variable for generic transformer method return types
T = TypeVar('T', bound=BaseModel)

logger = logging.getLogger(__name__)


class BaseTransformer(abc.ABC):
    """Base transformer class for converting API data to standardized models"""
    
    @abc.abstractmethod
    def transform_hotel_data(self, data: Dict[str, Any]) -> Hotel:
        """
        Transform hotel data from API response to standardized Hotel model
        
        Args:
            data: Hotel data from API response
            
        Returns:
            Standardized Hotel object
            
        Raises:
            TransformationError: If there's an issue with the data transformation
        """
        pass
    
    @abc.abstractmethod
    def transform_hotel_details(self, data: Dict[str, Any]) -> Hotel:
        """
        Transform detailed hotel data from API response to standardized Hotel model
        
        Args:
            data: Detailed hotel data from API response
            
        Returns:
            Standardized Hotel object with detailed information
            
        Raises:
            TransformationError: If there's an issue with the data transformation
        """
        pass
    
    @abc.abstractmethod
    def transform_room_data(self, data: Dict[str, Any], hotel_id: str) -> Room:
        """
        Transform room data from API response to standardized Room model
        
        Args:
            data: Room data from API response
            hotel_id: ID of the hotel this room belongs to
            
        Returns:
            Standardized Room object
            
        Raises:
            TransformationError: If there's an issue with the data transformation
        """
        pass
    
    @abc.abstractmethod
    def transform_booking_response(self, data: Dict[str, Any]) -> Booking:
        """
        Transform booking data from API response to standardized Booking model
        
        Args:
            data: Booking data from API response
            
        Returns:
            Standardized Booking object
            
        Raises:
            TransformationError: If there's an issue with the data transformation
        """
        pass
    
    @abc.abstractmethod
    def transform_booking_request(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform booking request data to API-specific format
        
        Args:
            data: Booking request data in standardized format
            
        Returns:
            Booking data in API-specific format
            
        Raises:
            TransformationError: If there's an issue with the data transformation
        """
        pass
    
    @abc.abstractmethod
    def transform_search_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform hotel search parameters to API-specific format
        
        Args:
            params: Search parameters in standardized format
            
        Returns:
            Search parameters in API-specific format
            
        Raises:
            TransformationError: If there's an issue with the data transformation
        """
        pass
    
    @abc.abstractmethod
    def transform_room_search_params(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Transform room search parameters to API-specific format
        
        Args:
            params: Room search parameters in standardized format
            
        Returns:
            Room search parameters in API-specific format
            
        Raises:
            TransformationError: If there's an issue with the data transformation
        """
        pass
