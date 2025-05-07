"""
Base adapter class that all API adapters will inherit from.
"""

import abc
import logging
from typing import Dict, Any, Optional, List, Type, TypeVar, Generic

from travel_connector.models.base import BaseModel
from travel_connector.models.hotel import Hotel
from travel_connector.models.room import Room
from travel_connector.models.booking import Booking
from travel_connector.utils.exceptions import AdapterError

# Type variable for generic adapter method return types
T = TypeVar('T', bound=BaseModel)

logger = logging.getLogger(__name__)


class BaseAdapter(abc.ABC):
    """Base adapter class for connecting to external travel APIs"""
    
    def __init__(self, api_key: str, api_url: str, timeout: int = 30):
        """
        Initialize the adapter with API credentials
        
        Args:
            api_key: Authentication key for the API
            api_url: Base URL for the API
            timeout: Request timeout in seconds
        """
        self.api_key = api_key
        self.api_url = api_url
        self.timeout = timeout
        self.source_name = self.__class__.__name__.replace('Adapter', '').lower()
        logger.info(f"Initialized {self.__class__.__name__} with base URL: {api_url}")
    
    @abc.abstractmethod
    def search_hotels(self, params: Dict[str, Any]) -> List[Hotel]:
        """
        Search for hotels based on given parameters
        
        Args:
            params: Search parameters (location, dates, guests, etc.)
            
        Returns:
            List of standardized Hotel objects
            
        Raises:
            AdapterError: If there's an issue with the API request or response
        """
        pass
    
    @abc.abstractmethod
    def get_hotel_details(self, hotel_id: str) -> Hotel:
        """
        Get detailed information for a specific hotel
        
        Args:
            hotel_id: Hotel identifier in the source system
            
        Returns:
            Standardized Hotel object with detailed information
            
        Raises:
            AdapterError: If there's an issue with the API request or response
        """
        pass
    
    @abc.abstractmethod
    def search_rooms(self, hotel_id: str, params: Dict[str, Any]) -> List[Room]:
        """
        Search for available rooms in a specific hotel
        
        Args:
            hotel_id: Hotel identifier in the source system
            params: Search parameters (dates, guests, etc.)
            
        Returns:
            List of standardized Room objects
            
        Raises:
            AdapterError: If there's an issue with the API request or response
        """
        pass
    
    @abc.abstractmethod
    def create_booking(self, booking_data: Dict[str, Any]) -> Booking:
        """
        Create a booking with the provider
        
        Args:
            booking_data: Booking details (hotel, room, guest info, etc.)
            
        Returns:
            Standardized Booking object
            
        Raises:
            AdapterError: If there's an issue with the API request or response
        """
        pass
    
    @abc.abstractmethod
    def get_booking(self, booking_id: str) -> Booking:
        """
        Get details of an existing booking
        
        Args:
            booking_id: Booking identifier in the source system
            
        Returns:
            Standardized Booking object
            
        Raises:
            AdapterError: If there's an issue with the API request or response
        """
        pass
    
    @abc.abstractmethod
    def cancel_booking(self, booking_id: str) -> Booking:
        """
        Cancel an existing booking
        
        Args:
            booking_id: Booking identifier in the source system
            
        Returns:
            Updated standardized Booking object
            
        Raises:
            AdapterError: If there's an issue with the API request or response
        """
        pass
    
    def get_hotel_dump(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Recupera il dump statico completo degli hotel
        
        Questo metodo sincronizzato restituisce tutti i dati sugli hotel disponibili nell'API.
        È possibile utilizzare i parametri di query per filtrare i risultati.
        
        Args:
            params: Parametri opzionali di filtraggio per il dump
            
        Returns:
            Dizionario contenente il dump completo degli hotel
            
        Raises:
            AdapterError: Se si verificano problemi con la richiesta API o la risposta
            NotImplementedError: Se l'adattatore non implementa questa funzione
        """
        raise NotImplementedError(f"L'adattatore {self.__class__.__name__} non implementa il metodo get_hotel_dump")
        
    def get_hotel_incremental_dump(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Recupera il dump incrementale degli hotel
        
        Questo metodo sincronizzato restituisce le modifiche agli hotel rispetto al giorno precedente
        o in base all'intervallo specificato. È possibile utilizzare i parametri di query per filtrare i risultati.
        
        Args:
            params: Parametri opzionali di filtraggio per il dump incrementale
            
        Returns:
            Dizionario contenente il dump incrementale degli hotel
            
        Raises:
            AdapterError: Se si verificano problemi con la richiesta API o la risposta
            NotImplementedError: Se l'adattatore non implementa questa funzione
        """
        raise NotImplementedError(f"L'adattatore {self.__class__.__name__} non implementa il metodo get_hotel_incremental_dump")
        
    def search_hotels_by_region(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cerca hotel in base alla regione specificata
        
        Questo metodo consente di cercare hotel in una regione geografica specifica,
        come un paese, una città o un'area particolare.
        
        Args:
            params: Parametri di ricerca, incluso l'ID della regione
            
        Returns:
            Dizionario contenente i risultati della ricerca
            
        Raises:
            AdapterError: Se si verificano problemi con la richiesta API o la risposta
            NotImplementedError: Se l'adattatore non implementa questa funzione
        """
        raise NotImplementedError(f"L'adattatore {self.__class__.__name__} non implementa il metodo search_hotels_by_region")
        
    def get_region_dump(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Recupera il dump completo delle regioni
        
        Questo metodo sincronizzato restituisce tutti i dati sulle regioni disponibili nell'API.
        È possibile utilizzare i parametri di query per filtrare i risultati.
        
        Args:
            params: Parametri opzionali di filtraggio per il dump delle regioni
            
        Returns:
            Dizionario contenente il dump completo delle regioni
            
        Raises:
            AdapterError: Se si verificano problemi con la richiesta API o la risposta
            NotImplementedError: Se l'adattatore non implementa questa funzione
        """
        raise NotImplementedError(f"L'adattatore {self.__class__.__name__} non implementa il metodo get_region_dump")
        
    def search_region_by_province(self, province_name: str, language: str = 'it', use_opensearch: bool = True) -> List[Dict[str, Any]]:
        """
        Cerca il region_id in base ad una provincia specificata
        
        Questo metodo consente di trovare l'identificativo di una regione (region_id) 
        cercando per nome di provincia.
        
        Args:
            province_name: Nome della provincia da cercare
            language: Codice lingua (default: 'it')
            use_opensearch: Se utilizzare OpenSearch quando disponibile (default: True)
            
        Returns:
            Lista di regioni trovate
            
        Raises:
            AdapterError: Se si verificano problemi con la richiesta API o la risposta
            NotImplementedError: Se l'adattatore non implementa questa funzione
        """
        raise NotImplementedError(f"L'adattatore {self.__class__.__name__} non implementa il metodo search_region_by_province")
    
    def _generate_model_id(self, source_id: str, model_type: Type[T]) -> str:
        """
        Generate a standardized ID for a model

        Args:
            source_id: Original ID from the source system
            model_type: Type of model (Hotel, Room, etc.)

        Returns:
            Standardized ID string
        """
        model_name = model_type.__name__.lower()
        return f"{self.source_name}_{model_name}_{source_id}"
