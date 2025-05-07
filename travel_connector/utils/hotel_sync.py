"""
Utilità per la sincronizzazione dei dati degli hotel da Ratehawk a OpenSearch

Questo modulo fornisce funzioni per:
1. Scaricare il dump completo degli hotel da Ratehawk
2. Decomprimere il file JSONL.zst
3. Filtrare gli hotel per paese (es. Italia)
4. Caricare i dati in OpenSearch per ricerche più efficienti
"""

import os
import json
import logging
import requests
import tempfile
from typing import Dict, Any, List, Optional

import zstandard as zstd
from opensearchpy import OpenSearch, helpers
from opensearchpy.exceptions import RequestError

from travel_connector.adapters.ratehawk_adapter import RatehawkAdapter

# Configurazione del logger
logger = logging.getLogger(__name__)

# Nome dell'indice OpenSearch per gli hotel
HOTEL_INDEX = "hotel_ratehawk"

# Configurazione di OpenSearch
OPENSEARCH_CONFIG = {
    'hosts': [{'host': os.environ.get('OPENSEARCH_HOST', 'localhost'), 
               'port': int(os.environ.get('OPENSEARCH_PORT', 9200))}],
    'http_auth': (os.environ.get('OPENSEARCH_USER', 'admin'), 
                 os.environ.get('OPENSEARCH_PASSWORD', 'admin')),
    'use_ssl': os.environ.get('OPENSEARCH_USE_SSL', 'false').lower() == 'true',
    'verify_certs': os.environ.get('OPENSEARCH_VERIFY_CERTS', 'false').lower() == 'true',
    'ssl_assert_hostname': False,
    'ssl_show_warn': False
}

# Mappatura dell'indice per gli hotel
HOTEL_INDEX_MAPPING = {
    "settings": {
        "number_of_shards": 1,
        "number_of_replicas": 0,
        "analysis": {
            "analyzer": {
                "custom_analyzer": {
                    "type": "custom",
                    "tokenizer": "standard",
                    "filter": ["lowercase", "asciifolding"]
                }
            }
        }
    },
    "mappings": {
        "properties": {
            "id": {"type": "keyword"},
            "name": {
                "type": "text",
                "analyzer": "custom_analyzer",
                "fields": {
                    "keyword": {"type": "keyword"}
                }
            },
            "address": {"type": "text", "analyzer": "custom_analyzer"},
            "country": {
                "properties": {
                    "name": {"type": "text", "analyzer": "custom_analyzer"},
                    "code": {"type": "keyword"}
                }
            },
            "region": {
                "properties": {
                    "id": {"type": "keyword"},
                    "name": {"type": "text", "analyzer": "custom_analyzer"}
                }
            },
            "stars": {"type": "float"},
            "rating": {"type": "float"},
            "photos": {"type": "keyword"},
            "description": {"type": "text", "analyzer": "custom_analyzer"},
            "amenities": {"type": "keyword"},
            "coordinates": {
                "type": "geo_point"
            }
        }
    }
}

def get_opensearch_client() -> OpenSearch:
    """
    Crea e restituisce un client OpenSearch configurato
    
    Returns:
        Client OpenSearch configurato
    """
    return OpenSearch(**OPENSEARCH_CONFIG)

def create_hotel_index(client: OpenSearch) -> bool:
    """
    Crea l'indice per gli hotel in OpenSearch se non esiste già
    
    Args:
        client: Client OpenSearch configurato
    
    Returns:
        True se l'indice è stato creato con successo o già esisteva, False altrimenti
    """
    try:
        # Verifica se l'indice esiste già
        if client.indices.exists(index=HOTEL_INDEX):
            logger.info(f"L'indice '{HOTEL_INDEX}' esiste già")
            return True
        
        # Crea l'indice con la mappatura specificata
        client.indices.create(index=HOTEL_INDEX, body=HOTEL_INDEX_MAPPING)
        logger.info(f"Indice '{HOTEL_INDEX}' creato con successo")
        return True
    
    except Exception as e:
        logger.error(f"Errore nella creazione dell'indice: {str(e)}")
        return False

def download_hotel_dump(url: str, output_file: str) -> bool:
    """
    Scarica il file di dump degli hotel dall'URL specificato
    
    Args:
        url: URL del file di dump
        output_file: Percorso del file di output
    
    Returns:
        True se il download è completato con successo, False altrimenti
    """
    try:
        logger.info(f"Download del dump degli hotel da: {url}")
        
        # Effettua la richiesta HTTP per il download
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Salva il file scaricato
        with open(output_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Download completato: {output_file}")
        return True
    
    except Exception as e:
        logger.error(f"Errore nel download del dump: {str(e)}")
        return False

def decompress_zst_file(input_file: str, output_file: str) -> bool:
    """
    Decomprime un file .zst in un file di testo
    
    Args:
        input_file: Percorso del file .zst compresso
        output_file: Percorso del file decompresso
    
    Returns:
        True se la decompressione è completata con successo, False altrimenti
    """
    try:
        logger.info(f"Decompressione del file {input_file}")
        
        # Decompressione del file
        with open(input_file, 'rb') as f_in:
            dctx = zstd.ZstdDecompressor()
            with open(output_file, 'wb') as f_out:
                dctx.copy_stream(f_in, f_out)
        
        logger.info(f"Decompressione completata: {output_file}")
        return True
    
    except Exception as e:
        logger.error(f"Errore nella decompressione: {str(e)}")
        return False

def filter_hotels_by_country(input_file: str, output_file: str, country_code: str) -> int:
    """
    Filtra gli hotel dal file JSONL per un paese specifico
    
    Args:
        input_file: Percorso del file JSONL decompresso
        output_file: Percorso del file di output filtrato
        country_code: Codice del paese per il filtraggio (es. "IT")
    
    Returns:
        Numero di hotel filtrati
    """
    try:
        logger.info(f"Filtraggio hotel per paese: {country_code}")
        
        count = 0
        with open(input_file, 'r', encoding='utf-8') as f_in:
            with open(output_file, 'w', encoding='utf-8') as f_out:
                for line in f_in:
                    try:
                        hotel = json.loads(line.strip())
                        if "country" in hotel and hotel.get("country", {}).get("code") == country_code:
                            f_out.write(line)
                            count += 1
                    except json.JSONDecodeError:
                        continue
        
        logger.info(f"Filtrati {count} hotel per il paese {country_code}")
        return count
    
    except Exception as e:
        logger.error(f"Errore nel filtraggio degli hotel: {str(e)}")
        return 0

def load_hotels_to_opensearch(input_file: str, client: OpenSearch) -> int:
    """
    Carica i dati degli hotel dal file JSONL a OpenSearch
    
    Args:
        input_file: Percorso del file JSONL con i dati degli hotel
        client: Client OpenSearch configurato
    
    Returns:
        Numero di hotel caricati con successo
    """
    try:
        logger.info(f"Caricamento hotel in OpenSearch dall'indice {HOTEL_INDEX}")
        
        # Generatore per il caricamento in bulk
        def generate_actions():
            with open(input_file, 'r', encoding='utf-8') as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        hotel = json.loads(line.strip())
                        
                        # Estrai e normalizza le coordinate se disponibili
                        coordinates = None
                        if "latitude" in hotel and "longitude" in hotel:
                            coordinates = {
                                "lat": float(hotel["latitude"]),
                                "lon": float(hotel["longitude"])
                            }
                        
                        # Prepara il documento per OpenSearch
                        doc = {
                            "_index": HOTEL_INDEX,
                            "_id": hotel.get("id"),
                            "_source": {
                                "id": hotel.get("id"),
                                "name": hotel.get("name"),
                                "address": hotel.get("address"),
                                "country": hotel.get("country"),
                                "region": hotel.get("region"),
                                "stars": hotel.get("stars"),
                                "rating": hotel.get("rating"),
                                "photos": hotel.get("photos", []),
                                "description": hotel.get("description"),
                                "amenities": hotel.get("amenities", [])
                            }
                        }
                        
                        # Aggiungi le coordinate solo se disponibili
                        if coordinates:
                            doc["_source"]["coordinates"] = coordinates
                        
                        yield doc
                        
                        if line_num % 1000 == 0:
                            logger.debug(f"Processate {line_num} righe")
                    
                    except json.JSONDecodeError as e:
                        logger.warning(f"Errore nel parsing della riga {line_num}: {str(e)}")
                        continue
        
        # Esegui il caricamento bulk
        success, errors = helpers.bulk(client, generate_actions(), stats_only=True)
        
        logger.info(f"Caricamento completato: {success} hotel inseriti, {len(errors) if errors else 0} errori")
        return success
    
    except Exception as e:
        logger.error(f"Errore nel caricamento degli hotel in OpenSearch: {str(e)}")
        return 0

def search_hotels_by_name(query: str, client: Optional[OpenSearch] = None) -> List[Dict[str, Any]]:
    """
    Cerca hotel per nome in OpenSearch
    
    Args:
        query: Nome dell'hotel da cercare
        client: Client OpenSearch opzionale (se None, ne viene creato uno nuovo)
    
    Returns:
        Lista di hotel che corrispondono alla query
    """
    try:
        # Crea un client se non è stato fornito
        if client is None:
            client = get_opensearch_client()
        
        # Preparazione della query di ricerca
        search_query = {
            "query": {
                "bool": {
                    "should": [
                        {"match": {"name": {"query": query, "boost": 2.0}}},
                        {"match": {"address": query}},
                        {"match": {"description": query}}
                    ]
                }
            },
            "size": 10
        }
        
        # Esecuzione della ricerca
        response = client.search(index=HOTEL_INDEX, body=search_query)
        
        # Estrazione e formattazione dei risultati
        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            results.append({
                "id": source.get("id"),
                "name": source.get("name"),
                "address": source.get("address"),
                "country": source.get("country"),
                "region": source.get("region"),
                "stars": source.get("stars"),
                "rating": source.get("rating"),
                "score": hit.get("_score")
            })
        
        return results
    
    except Exception as e:
        logger.error(f"Errore nella ricerca degli hotel: {str(e)}")
        return []

def search_hotels_by_region(region_id: str, client: Optional[OpenSearch] = None) -> List[Dict[str, Any]]:
    """
    Cerca hotel per ID regione in OpenSearch
    
    Args:
        region_id: ID della regione
        client: Client OpenSearch opzionale (se None, ne viene creato uno nuovo)
    
    Returns:
        Lista di hotel nella regione specificata
    """
    try:
        # Crea un client se non è stato fornito
        if client is None:
            client = get_opensearch_client()
        
        # Preparazione della query di ricerca
        search_query = {
            "query": {
                "term": {
                    "region.id": region_id
                }
            },
            "size": 50
        }
        
        # Esecuzione della ricerca
        response = client.search(index=HOTEL_INDEX, body=search_query)
        
        # Estrazione e formattazione dei risultati
        results = []
        for hit in response["hits"]["hits"]:
            source = hit["_source"]
            results.append({
                "id": source.get("id"),
                "name": source.get("name"),
                "address": source.get("address"),
                "country": source.get("country"),
                "region": source.get("region"),
                "stars": source.get("stars"),
                "rating": source.get("rating")
            })
        
        return results
    
    except Exception as e:
        logger.error(f"Errore nella ricerca degli hotel per regione: {str(e)}")
        return []

def sync_hotels_from_ratehawk(adapter: RatehawkAdapter, country_code: str = "IT") -> bool:
    """
    Sincronizza gli hotel da Ratehawk a OpenSearch
    
    Args:
        adapter: Istanza configurata di RatehawkAdapter
        country_code: Codice del paese per filtrare gli hotel (default: "IT" per Italia)
    
    Returns:
        True se la sincronizzazione è completata con successo, False altrimenti
    """
    try:
        logger.info(f"Avvio sincronizzazione hotel da Ratehawk a OpenSearch")
        
        # Parametri per il dump degli hotel
        params = {
            "inventory": "all",
            "language": "it",
            "country_codes": [country_code]
        }
        
        # Ottieni il dump degli hotel (URL del file .zst)
        dump_result = adapter.get_hotel_dump(params)
        
        if not dump_result or "data" not in dump_result or "url" not in dump_result["data"]:
            logger.error("Impossibile ottenere l'URL del dump degli hotel")
            return False
        
        # URL del file di dump
        dump_url = dump_result["data"]["url"]
        
        # Crea directory temporanee per i file
        with tempfile.TemporaryDirectory() as temp_dir:
            # Percorsi dei file temporanei
            compressed_file = os.path.join(temp_dir, "hotels.jsonl.zst")
            decompressed_file = os.path.join(temp_dir, "hotels.jsonl")
            filtered_file = os.path.join(temp_dir, f"hotels_{country_code}.jsonl")
            
            # Download del file
            if not download_hotel_dump(dump_url, compressed_file):
                return False
            
            # Decompressione del file
            if not decompress_zst_file(compressed_file, decompressed_file):
                return False
            
            # Filtraggio degli hotel per paese
            filtered_count = filter_hotels_by_country(decompressed_file, filtered_file, country_code)
            if filtered_count == 0:
                logger.warning(f"Nessun hotel trovato per il paese {country_code}")
                return False
            
            # Caricamento in OpenSearch
            client = get_opensearch_client()
            
            # Crea l'indice se non esiste
            if not create_hotel_index(client):
                return False
            
            # Carica gli hotel in OpenSearch
            loaded_count = load_hotels_to_opensearch(filtered_file, client)
            
            logger.info(f"Sincronizzazione completata: {loaded_count} hotel caricati in OpenSearch")
            return loaded_count > 0
    
    except Exception as e:
        logger.error(f"Errore durante la sincronizzazione degli hotel: {str(e)}")
        return False

def check_opensearch_status() -> Dict[str, Any]:
    """
    Verifica lo stato della connessione a OpenSearch e dell'indice degli hotel
    
    Returns:
        Dizionario con lo stato della connessione e dell'indice
    """
    try:
        client = get_opensearch_client()
        
        # Verifica la connessione
        health = client.cluster.health()
        
        # Verifica l'indice
        index_exists = client.indices.exists(index=HOTEL_INDEX)
        
        # Se l'indice esiste, recupera il conteggio dei documenti
        doc_count = 0
        if index_exists:
            index_stats = client.indices.stats(index=HOTEL_INDEX)
            doc_count = index_stats["indices"][HOTEL_INDEX]["total"]["docs"]["count"]
        
        return {
            "connected": True,
            "cluster_name": health.get("cluster_name"),
            "status": health.get("status"),
            "hotel_index_exists": index_exists,
            "hotel_count": doc_count
        }
    
    except Exception as e:
        logger.error(f"Errore nella verifica dello stato di OpenSearch: {str(e)}")
        return {
            "connected": False,
            "error": str(e)
        }