"""
Main module for the travel connector package providing factory functions
for creating adapters and interacting with the standardized data model.
"""

import os
import logging
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional, Type, Union

# Carica variabili d'ambiente dal file .env
load_dotenv()

from travel_connector.adapters.base_adapter import BaseAdapter
from travel_connector.adapters.ratehawk_adapter import RatehawkAdapter
from travel_connector.models.hotel import Hotel
from travel_connector.models.room import Room
from travel_connector.models.booking import Booking
from travel_connector.models.location import Location
from travel_connector.config import get_config, get_api_key, get_key_id
from travel_connector.utils.exceptions import ConfigurationError

logger = logging.getLogger(__name__)


class TravelConnector:
    """Main connector class for accessing travel data APIs"""
    
    def __init__(self):
        """Initialize the travel connector with available adapters"""
        self.config = get_config()
        self.adapters = {}
        logger.info("Initialized TravelConnector")
    
    def register_adapter(self, name: str, adapter: BaseAdapter) -> None:
        """
        Register an adapter for a specific data source
        
        Args:
            name: Name identifier for the adapter
            adapter: Adapter instance
        """
        self.adapters[name] = adapter
        logger.info(f"Registered adapter: {name}")
    
    def get_adapter(self, name: str) -> BaseAdapter:
        """
        Get a registered adapter by name
        
        Args:
            name: Name of the adapter to retrieve
            
        Returns:
            The adapter instance
            
        Raises:
            ConfigurationError: If the adapter is not registered
        """
        if name not in self.adapters:
            logger.error(f"Adapter '{name}' not registered")
            raise ConfigurationError(f"Adapter '{name}' not registered")
        return self.adapters[name]
    
    def search_hotels(self, source: str, params: Dict[str, Any]) -> List[Hotel]:
        """
        Search for hotels using a specific adapter
        
        Args:
            source: Name of the data source adapter to use
            params: Search parameters
            
        Returns:
            List of standardized Hotel objects
        """
        adapter = self.get_adapter(source)
        return adapter.search_hotels(params)
    
    def get_hotel_details(self, source: str, hotel_id: str) -> Hotel:
        """
        Get detailed information for a specific hotel
        
        Args:
            source: Name of the data source adapter to use
            hotel_id: Hotel identifier
            
        Returns:
            Standardized Hotel object with detailed information
        """
        adapter = self.get_adapter(source)
        return adapter.get_hotel_details(hotel_id)
    
    def search_rooms(self, source: str, hotel_id: str, params: Dict[str, Any]) -> List[Room]:
        """
        Search for available rooms in a specific hotel
        
        Args:
            source: Name of the data source adapter to use
            hotel_id: Hotel identifier
            params: Search parameters
            
        Returns:
            List of standardized Room objects
        """
        adapter = self.get_adapter(source)
        return adapter.search_rooms(hotel_id, params)
    
    def create_booking(self, source: str, booking_data: Dict[str, Any]) -> Booking:
        """
        Create a booking with a specific provider
        
        Args:
            source: Name of the data source adapter to use
            booking_data: Booking details
            
        Returns:
            Standardized Booking object
        """
        adapter = self.get_adapter(source)
        return adapter.create_booking(booking_data)
    
    def get_booking(self, source: str, booking_id: str) -> Booking:
        """
        Get details of an existing booking
        
        Args:
            source: Name of the data source adapter to use
            booking_id: Booking identifier
            
        Returns:
            Standardized Booking object
        """
        adapter = self.get_adapter(source)
        return adapter.get_booking(booking_id)
    
    def cancel_booking(self, source: str, booking_id: str) -> Booking:
        """
        Cancel an existing booking
        
        Args:
            source: Name of the data source adapter to use
            booking_id: Booking identifier
            
        Returns:
            Updated standardized Booking object
        """
        adapter = self.get_adapter(source)
        return adapter.cancel_booking(booking_id)
    
    def get_hotel_dump(self, source: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Recupera il dump statico completo degli hotel
        
        Questa funzione è sincronizzata e restituisce tutti i dati degli hotel disponibili dall'API.
        In base al fornitore, i dati disponibili nel dump potrebbero variare.
        
        Args:
            source: Nome dell'adattatore del fornitore da utilizzare
            params: Parametri opzionali per filtrare i risultati del dump
            
        Returns:
            Dizionario contenente il dump completo degli hotel
            
        Raises:
            ConfigurationError: Se l'adattatore specificato non è registrato
            AdapterError: Se si verificano problemi con la richiesta API o la risposta
        """
        adapter = self.get_adapter(source)
        
        # Verifica che l'adattatore implementi il metodo get_hotel_dump
        if not hasattr(adapter, 'get_hotel_dump'):
            logger.error(f"L'adattatore '{source}' non supporta il metodo get_hotel_dump")
            raise ConfigurationError(f"L'adattatore '{source}' non supporta il metodo get_hotel_dump")
        
        return adapter.get_hotel_dump(params)
        
    def get_hotel_incremental_dump(self, source: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Recupera il dump incrementale degli hotel
        
        Questa funzione è sincronizzata e restituisce le modifiche agli hotel rispetto al giorno precedente
        o in base all'intervallo specificato. In base al fornitore, i dati disponibili potrebbero variare.
        
        Args:
            source: Nome dell'adattatore del fornitore da utilizzare
            params: Parametri opzionali per filtrare i risultati del dump incrementale
            
        Returns:
            Dizionario contenente il dump incrementale degli hotel
            
        Raises:
            ConfigurationError: Se l'adattatore specificato non è registrato o non supporta questa funzionalità
            AdapterError: Se si verificano problemi con la richiesta API o la risposta
        """
        adapter = self.get_adapter(source)
        
        # Verifica che l'adattatore implementi il metodo get_hotel_incremental_dump
        if not hasattr(adapter, 'get_hotel_incremental_dump'):
            logger.error(f"L'adattatore '{source}' non supporta il metodo get_hotel_incremental_dump")
            raise ConfigurationError(f"L'adattatore '{source}' non supporta il metodo get_hotel_incremental_dump")
        
        return adapter.get_hotel_incremental_dump(params)
        
    def search_hotels_by_region(self, source: str, params: Dict[str, Any], use_opensearch: bool = True) -> Dict[str, Any]:
        """
        Cerca hotel in base alla regione specificata
        
        Questa funzione consente di cercare hotel in una regione geografica specifica,
        come un paese, una città o un'area particolare.
        
        Args:
            source: Nome dell'adattatore del fornitore da utilizzare
            params: Parametri di ricerca, deve includere l'ID della regione
            use_opensearch: Se utilizzare OpenSearch quando disponibile (default: True)
            
        Returns:
            Dizionario contenente i risultati della ricerca
            
        Raises:
            ConfigurationError: Se l'adattatore specificato non è registrato o non supporta questa funzionalità
            AdapterError: Se si verificano problemi con la richiesta API o la risposta
            ValueError: Se mancano parametri obbligatori
        """
        adapter = self.get_adapter(source)
        
        # Verifica che l'adattatore implementi il metodo search_hotels_by_region
        if not hasattr(adapter, 'search_hotels_by_region'):
            logger.error(f"L'adattatore '{source}' non supporta il metodo search_hotels_by_region")
            raise ConfigurationError(f"L'adattatore '{source}' non supporta il metodo search_hotels_by_region")
        
        # Chiama il metodo con il parametro aggiuntivo use_opensearch
        if hasattr(adapter.search_hotels_by_region, '__code__') and adapter.search_hotels_by_region.__code__.co_argcount > 2:
            return adapter.search_hotels_by_region(params, use_opensearch)
        else:
            # Fallback per vecchie implementazioni dell'adapter che non accettano use_opensearch
            logger.warning(f"L'adattatore '{source}' utilizza una versione precedente del metodo search_hotels_by_region che non supporta OpenSearch")
            return adapter.search_hotels_by_region(params)
        
    def get_region_dump(self, source: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Recupera il dump completo delle regioni
        
        Questa funzione è sincronizzata e restituisce tutti i dati sulle regioni disponibili nell'API.
        Il dump completo può essere utilizzato per analisi, cache locale o per costruire una mappa 
        di riferimento region_id -> nome della regione.
        
        Args:
            source: Nome dell'adattatore del fornitore da utilizzare
            params: Parametri opzionali per filtrare i risultati del dump regioni
            
        Returns:
            Dizionario contenente il dump completo delle regioni
            
        Raises:
            ConfigurationError: Se l'adattatore specificato non è registrato o non supporta questa funzionalità
            AdapterError: Se si verificano problemi con la richiesta API o la risposta
        """
        adapter = self.get_adapter(source)
        
        # Verifica che l'adattatore implementi il metodo get_region_dump
        if not hasattr(adapter, 'get_region_dump'):
            logger.error(f"L'adattatore '{source}' non supporta il metodo get_region_dump")
            raise ConfigurationError(f"L'adattatore '{source}' non supporta il metodo get_region_dump")
        
        return adapter.get_region_dump(params)
    
    def search_region_by_province(self, source: str, province_name: str, language: str = 'it', use_opensearch: bool = True) -> List[Dict[str, Any]]:
        """
        Cerca il region_id in base ad una provincia specificata
        
        Questa funzione consente di trovare l'identificativo di una regione (region_id) 
        cercando per nome di provincia. Utile per ottenere il region_id da utilizzare 
        nella funzione search_hotels_by_region.
        
        Args:
            source: Nome dell'adattatore del fornitore da utilizzare
            province_name: Nome della provincia da cercare
            language: Codice lingua (default: 'it')
            use_opensearch: Se utilizzare OpenSearch quando disponibile (default: True)
            
        Returns:
            Lista di regioni trovate che corrispondono alla provincia
            
        Raises:
            ConfigurationError: Se l'adattatore specificato non è registrato o non supporta questa funzionalità
            AdapterError: Se si verificano problemi con la richiesta API o la risposta
        """
        adapter = self.get_adapter(source)
        
        # Verifica che l'adattatore implementi il metodo search_region_by_province
        if not hasattr(adapter, 'search_region_by_province'):
            logger.error(f"L'adattatore '{source}' non supporta il metodo search_region_by_province")
            raise ConfigurationError(f"L'adattatore '{source}' non supporta il metodo search_region_by_province")
        
        return adapter.search_region_by_province(province_name, language, use_opensearch)
    
    def search_hotels_by_name(self, source: str, hotel_name: str, language: str = 'it', use_opensearch: bool = True) -> List[Dict[str, Any]]:
        """
        Cerca hotel in base al nome specificato
        
        Questa funzione consente di trovare hotel cercando per nome. La ricerca è ottimizzata
        per trovare corrispondenze anche parziali.
        
        Args:
            source: Nome dell'adattatore del fornitore da utilizzare
            hotel_name: Nome dell'hotel da cercare
            language: Codice lingua (default: 'it')
            use_opensearch: Se utilizzare OpenSearch quando disponibile (default: True)
            
        Returns:
            Lista di hotel trovati che corrispondono al nome
            
        Raises:
            ConfigurationError: Se l'adattatore specificato non è registrato o non supporta questa funzionalità
            AdapterError: Se si verificano problemi con la richiesta API o la risposta
        """
        adapter = self.get_adapter(source)
        
        # Verifica che l'adattatore implementi il metodo search_hotels_by_name
        if not hasattr(adapter, 'search_hotels_by_name'):
            logger.error(f"L'adattatore '{source}' non supporta il metodo search_hotels_by_name")
            raise ConfigurationError(f"L'adattatore '{source}' non supporta il metodo search_hotels_by_name")
        
        return adapter.search_hotels_by_name(hotel_name, language, use_opensearch)
    
    def check_opensearch_status(self) -> Dict[str, Any]:
        """
        Verifica lo stato della connessione a OpenSearch e degli indici
        
        Questa funzione controlla la connessione a OpenSearch e verifica lo stato
        degli indici delle regioni e degli hotel.
        
        Returns:
            Dizionario contenente lo stato della connessione e degli indici
            
        Raises:
            Exception: Se si verificano problemi con la verifica
        """
        try:
            from travel_connector.utils.opensearch_client import check_opensearch_connection, check_indices_status
            
            # Verifica la connessione di base
            connection_status = check_opensearch_connection()
            
            # Se la connessione è attiva, verifica gli indici
            if connection_status.get("status") == "connected":
                indices_status = check_indices_status()
                connection_status["indices"] = indices_status
            
            return connection_status
            
        except Exception as e:
            logger.error(f"Errore nella verifica dello stato di OpenSearch: {str(e)}")
            return {
                "status": "error",
                "message": str(e)
            }


def create_connector() -> TravelConnector:
    """
    Factory function to create and configure a TravelConnector instance
    
    Returns:
        Configured TravelConnector instance
    """
    connector = TravelConnector()
    
    try:
        # Configure Ratehawk adapter
        ratehawk_config = connector.config["apis"]["ratehawk"]
        ratehawk_api_key = get_api_key("ratehawk")
        ratehawk_key_id = get_key_id("ratehawk")
        
        # Log che viene utilizzato KEY_ID=5412
        logger.info(f"Using Ratehawk with KEY_ID: {ratehawk_key_id}")
        
        ratehawk_adapter = RatehawkAdapter(
            api_key=ratehawk_api_key,
            api_url=ratehawk_config["api_url"],
            key_id=ratehawk_key_id,
            timeout=ratehawk_config["timeout"]
        )
        connector.register_adapter("ratehawk", ratehawk_adapter)
        
        # Additional adapters can be configured here as they are implemented
        
        return connector
        
    except Exception as e:
        logger.error(f"Failed to create connector: {str(e)}")
        raise ConfigurationError(f"Failed to create connector: {str(e)}")
