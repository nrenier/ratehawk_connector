"""
Client per interagire con OpenSearch.

Questo modulo fornisce funzioni per:
1. Creare una connessione a OpenSearch
2. Eseguire query di ricerca per regioni e hotel
3. Gestire le operazioni sugli indici
4. Verificare lo stato della connessione
"""

import os
import json
import logging
from typing import Dict, List, Any, Optional, Union

from opensearchpy import OpenSearch
from travel_connector.utils.exceptions import SyncError

logger = logging.getLogger(__name__)


def get_opensearch_client(config: Optional[Dict[str, Any]] = None) -> OpenSearch:
    """
    Crea un client OpenSearch con la configurazione specificata o predefinita.
    
    Args:
        config: Configurazione per OpenSearch (opzionale)
    
    Returns:
        Client OpenSearch configurato
    
    Raises:
        SyncError: Se c'è un problema con la creazione del client
    """
    try:
        if config is None:
            config = {
                'hosts': [{
                    'host': os.environ.get('OPENSEARCH_HOST', 'localhost'),
                    'port': int(os.environ.get('OPENSEARCH_PORT', 9200))
                }],
                'auth': (
                    os.environ.get('OPENSEARCH_USER', 'admin'),
                    os.environ.get('OPENSEARCH_PASSWORD', 'admin')
                ),
                'use_ssl': os.environ.get('OPENSEARCH_USE_SSL', 'false').lower() == 'true',
                'verify_certs': os.environ.get('OPENSEARCH_VERIFY_CERTS', 'false').lower() == 'true',
                'ssl_assert_hostname': False,
                'ssl_show_warn': False
            }
        
        return OpenSearch(
            hosts=config.get('hosts', [{'host': 'localhost', 'port': 9200}]),
            http_auth=config.get('auth', None),
            use_ssl=config.get('use_ssl', False),
            verify_certs=config.get('verify_certs', False),
            ssl_assert_hostname=config.get('ssl_assert_hostname', False),
            ssl_show_warn=config.get('ssl_show_warn', False)
        )
    
    except Exception as e:
        logger.error(f"Errore nella creazione del client OpenSearch: {str(e)}")
        raise SyncError(f"Errore nella creazione del client OpenSearch: {str(e)}")


def search_regions_by_province(province_name: str, index_name: str = 'region_italy_ratehawk', 
                               config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Cerca regioni in OpenSearch in base al nome della provincia.
    
    Args:
        province_name: Nome della provincia da cercare
        index_name: Nome dell'indice OpenSearch
        config: Configurazione per OpenSearch (opzionale)
    
    Returns:
        Lista di regioni che corrispondono alla ricerca
    
    Raises:
        SyncError: Se c'è un problema con la ricerca
    """
    try:
        # Crea il client OpenSearch
        client = get_opensearch_client(config)
        
        # Costruisci la query
        query = {
            "size": 10,  # Limita i risultati
            "query": {
                "bool": {
                    "should": [
                        # Cerca corrispondenze esatte nel campo name.keyword
                        {
                            "match_phrase": {
                                "name": province_name
                            }
                        },
                        # Cerca corrispondenze parziali nel campo name
                        {
                            "match": {
                                "name": {
                                    "query": province_name,
                                    "fuzziness": "AUTO"
                                }
                            }
                        }
                    ],
                    "filter": [
                        # Filtra per tipo: state o city
                        {
                            "terms": {
                                "type": ["state", "city"]
                            }
                        },
                        # Filtra per regioni che hanno hotel
                        {
                            "range": {
                                "hotels_number": {
                                    "gt": 0
                                }
                            }
                        }
                    ]
                }
            },
            # Ordina per rilevanza e poi per numero di hotel
            "sort": [
                "_score",
                {"hotels_number": {"order": "desc"}}
            ]
        }
        
        # Esegui la ricerca
        if not client.indices.exists(index=index_name):
            logger.warning(f"L'indice {index_name} non esiste. Ritorno una lista vuota.")
            return []
        
        response = client.search(
            body=query,
            index=index_name
        )
        
        # Elabora i risultati
        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            
            # Formatta il risultato in modo coerente con l'API Ratehawk
            region = {
                "id": source.get("id"),
                "name": source.get("name"),
                "type": source.get("type"),
                "country": source.get("country", {"name": "Italia", "code": "IT"}),
                "hotels_count": source.get("hotels_number", 0)
            }
            
            # Aggiungi le coordinate se disponibili
            if "center" in source:
                region["coordinates"] = {
                    "lat": source["center"].get("lat"),
                    "lon": source["center"].get("lon")
                }
            
            results.append(region)
        
        # Chiudi la connessione
        client.close()
        
        logger.info(f"Trovate {len(results)} regioni per la provincia '{province_name}' in OpenSearch")
        return results
        
    except Exception as e:
        logger.error(f"Errore nella ricerca di regioni per provincia in OpenSearch: {str(e)}")
        raise SyncError(f"Errore nella ricerca di regioni in OpenSearch: {str(e)}")


def check_opensearch_connection(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Verifica la connessione a OpenSearch.
    
    Args:
        config: Configurazione per OpenSearch (opzionale)
    
    Returns:
        Risultato della verifica
    """
    try:
        client = get_opensearch_client(config)
        info = client.info()
        client.close()
        
        return {
            "status": "connected",
            "version": info.get("version", {}).get("number", "unknown"),
            "cluster_name": info.get("cluster_name", "unknown")
        }
    except Exception as e:
        logger.error(f"Errore nella connessione a OpenSearch: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }


def search_hotels_by_name(hotel_name: str, index_name: str = 'hotel_ratehawk',
                         config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Cerca hotel in OpenSearch in base al nome.
    
    Args:
        hotel_name: Nome dell'hotel da cercare
        index_name: Nome dell'indice OpenSearch
        config: Configurazione per OpenSearch (opzionale)
    
    Returns:
        Lista di hotel che corrispondono alla ricerca
    
    Raises:
        SyncError: Se c'è un problema con la ricerca
    """
    try:
        # Crea il client OpenSearch
        client = get_opensearch_client(config)
        
        # Costruisci la query
        query = {
            "size": 10,  # Limita i risultati
            "query": {
                "bool": {
                    "should": [
                        # Cerca corrispondenze esatte
                        {
                            "match_phrase": {
                                "name": hotel_name
                            }
                        },
                        # Cerca corrispondenze parziali con fuzzy matching
                        {
                            "match": {
                                "name": {
                                    "query": hotel_name,
                                    "fuzziness": "AUTO"
                                }
                            }
                        },
                        # Cerca nell'indirizzo
                        {
                            "match": {
                                "address": hotel_name
                            }
                        }
                    ]
                }
            },
            # Ordina per rilevanza e poi per valutazione
            "sort": [
                "_score",
                {"rating": {"order": "desc"}}
            ]
        }
        
        # Esegui la ricerca
        if not client.indices.exists(index=index_name):
            logger.warning(f"L'indice {index_name} non esiste. Ritorno una lista vuota.")
            return []
        
        response = client.search(
            body=query,
            index=index_name
        )
        
        # Elabora i risultati
        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            
            # Formatta il risultato in modo coerente
            hotel = {
                "id": source.get("id"),
                "name": source.get("name"),
                "address": source.get("address"),
                "country": source.get("country", {"name": "Italia", "code": "IT"}),
                "region": source.get("region", {}),
                "stars": source.get("stars"),
                "rating": source.get("rating"),
                "score": hit.get("_score")
            }
            
            # Aggiungi le coordinate se disponibili
            if "coordinates" in source:
                hotel["coordinates"] = source["coordinates"]
            
            results.append(hotel)
        
        # Chiudi la connessione
        client.close()
        
        logger.info(f"Trovati {len(results)} hotel per la query '{hotel_name}' in OpenSearch")
        return results
        
    except Exception as e:
        logger.error(f"Errore nella ricerca di hotel per nome in OpenSearch: {str(e)}")
        raise SyncError(f"Errore nella ricerca di hotel in OpenSearch: {str(e)}")


def search_hotels_by_region(region_id: str, index_name: str = 'hotel_ratehawk',
                           config: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
    """
    Cerca hotel in OpenSearch in base all'ID della regione.
    
    Args:
        region_id: ID della regione
        index_name: Nome dell'indice OpenSearch
        config: Configurazione per OpenSearch (opzionale)
    
    Returns:
        Lista di hotel nella regione specificata
    
    Raises:
        SyncError: Se c'è un problema con la ricerca
    """
    try:
        # Crea il client OpenSearch
        client = get_opensearch_client(config)
        
        # Costruisci la query
        query = {
            "size": 50,  # Limita i risultati ai primi 50 hotel
            "query": {
                "term": {
                    "region.id": region_id
                }
            },
            # Ordina per valutazione (decrescente) e numero di stelle
            "sort": [
                {"rating": {"order": "desc"}},
                {"stars": {"order": "desc"}}
            ]
        }
        
        # Esegui la ricerca
        if not client.indices.exists(index=index_name):
            logger.warning(f"L'indice {index_name} non esiste. Ritorno una lista vuota.")
            return []
        
        response = client.search(
            body=query,
            index=index_name
        )
        
        # Elabora i risultati
        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            
            # Formatta il risultato in modo coerente
            hotel = {
                "id": source.get("id"),
                "name": source.get("name"),
                "address": source.get("address"),
                "country": source.get("country", {"name": "Italia", "code": "IT"}),
                "region": source.get("region", {}),
                "stars": source.get("stars"),
                "rating": source.get("rating")
            }
            
            # Aggiungi le coordinate se disponibili
            if "coordinates" in source:
                hotel["coordinates"] = source["coordinates"]
            
            results.append(hotel)
        
        # Chiudi la connessione
        client.close()
        
        logger.info(f"Trovati {len(results)} hotel nella regione '{region_id}' in OpenSearch")
        return results
        
    except Exception as e:
        logger.error(f"Errore nella ricerca di hotel per regione in OpenSearch: {str(e)}")
        raise SyncError(f"Errore nella ricerca di hotel per regione in OpenSearch: {str(e)}")


def check_indices_status(config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Verifica lo stato degli indici in OpenSearch.
    
    Args:
        config: Configurazione per OpenSearch (opzionale)
    
    Returns:
        Stato degli indici
    """
    try:
        client = get_opensearch_client(config)
        
        # Indici da verificare
        indices = ['region_italy_ratehawk', 'hotel_ratehawk']
        result = {}
        
        for index in indices:
            if client.indices.exists(index=index):
                stats = client.indices.stats(index=index)
                count = stats["indices"][index]["total"]["docs"]["count"]
                result[index] = {
                    "exists": True,
                    "doc_count": count
                }
            else:
                result[index] = {
                    "exists": False,
                    "doc_count": 0
                }
        
        client.close()
        return result
    
    except Exception as e:
        logger.error(f"Errore nella verifica degli indici: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }