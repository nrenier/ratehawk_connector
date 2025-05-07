"""
Utilità per sincronizzare i dati delle regioni da Ratehawk/WorldOta a OpenSearch.

Questo modulo fornisce funzioni per:
1. Scaricare il dump completo delle regioni da Ratehawk
2. Decomprimere il file zstd
3. Filtrare i dati per le regioni italiane (country_code: IT)
4. Caricare i dati filtrati in OpenSearch
"""

import os
import json
import logging
import requests
import zstandard as zstd
from typing import Dict, List, Any, Optional

from opensearchpy import OpenSearch, helpers
from travel_connector.utils.exceptions import SyncError

logger = logging.getLogger(__name__)


def download_region_dump(url: str, output_path: str) -> str:
    """
    Scarica il file di dump delle regioni da un URL
    
    Args:
        url: URL del file di dump (ottenuto dalla risposta dell'API)
        output_path: Percorso dove salvare il file scaricato
        
    Returns:
        Percorso del file scaricato
        
    Raises:
        SyncError: Se c'è un problema con il download del file
    """
    try:
        logger.info(f"Downloading region dump from {url}")
        
        # Crea la directory di output se non esiste
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Scarica il file
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Salva il file
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        logger.info(f"Downloaded region dump to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error downloading region dump: {str(e)}")
        raise SyncError(f"Error downloading region dump: {str(e)}")


def decompress_zstd_file(input_path: str, output_path: str) -> str:
    """
    Decomprime un file zstd
    
    Args:
        input_path: Percorso del file compresso
        output_path: Percorso dove salvare il file decompresso
        
    Returns:
        Percorso del file decompresso
        
    Raises:
        SyncError: Se c'è un problema con la decompressione del file
    """
    try:
        logger.info(f"Decompressing {input_path} to {output_path}")
        
        # Crea la directory di output se non esiste
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Decomprime il file
        with open(input_path, 'rb') as compressed:
            decompressor = zstd.ZstdDecompressor()
            with open(output_path, 'wb') as destination:
                decompressor.copy_stream(compressed, destination)
        
        logger.info(f"Decompressed file to {output_path}")
        return output_path
        
    except Exception as e:
        logger.error(f"Error decompressing file: {str(e)}")
        raise SyncError(f"Error decompressing file: {str(e)}")


def filter_italian_regions(input_path: str, output_path: str) -> str:
    """
    Filtra il file JSONL per estrarre solo le regioni italiane
    
    Args:
        input_path: Percorso del file JSONL decompresso
        output_path: Percorso dove salvare il file filtrato
        
    Returns:
        Percorso del file filtrato
        
    Raises:
        SyncError: Se c'è un problema con il filtering del file
    """
    try:
        logger.info(f"Filtering Italian regions from {input_path}")
        
        # Crea la directory di output se non esiste
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        count_total = 0
        count_italian = 0
        
        # Filtra le regioni italiane
        with open(input_path, 'r', encoding='utf-8') as infile, \
             open(output_path, 'w', encoding='utf-8') as outfile:
            for line in infile:
                count_total += 1
                try:
                    region = json.loads(line.strip())
                    # Verifica se la regione è italiana
                    if region.get('country', {}).get('code') == 'IT':
                        outfile.write(line)
                        count_italian += 1
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON line: {line[:100]}...")
                    continue
        
        logger.info(f"Filtered {count_italian} Italian regions out of {count_total} total regions")
        return output_path
        
    except Exception as e:
        logger.error(f"Error filtering Italian regions: {str(e)}")
        raise SyncError(f"Error filtering Italian regions: {str(e)}")


def load_regions_to_opensearch(
    input_path: str, 
    index_name: str, 
    opensearch_config: Dict[str, Any],
    batch_size: int = 1000
) -> int:
    """
    Carica i dati delle regioni in OpenSearch
    
    Args:
        input_path: Percorso del file JSONL filtrato
        index_name: Nome dell'indice OpenSearch
        opensearch_config: Configurazione della connessione OpenSearch
        batch_size: Dimensione del batch per l'upload in bulk
        
    Returns:
        Numero di documenti caricati
        
    Raises:
        SyncError: Se c'è un problema con il caricamento dei dati
    """
    try:
        logger.info(f"Loading regions to OpenSearch index '{index_name}'")
        
        # Crea il client OpenSearch
        client = OpenSearch(
            hosts=opensearch_config.get('hosts', [{'host': 'localhost', 'port': 9200}]),
            http_auth=opensearch_config.get('auth', None),
            use_ssl=opensearch_config.get('use_ssl', False),
            verify_certs=opensearch_config.get('verify_certs', False),
            ssl_assert_hostname=opensearch_config.get('ssl_assert_hostname', False),
            ssl_show_warn=opensearch_config.get('ssl_show_warn', False)
        )
        
        # Crea l'indice se non esiste
        if not client.indices.exists(index=index_name):
            client.indices.create(
                index=index_name,
                body={
                    "mappings": {
                        "properties": {
                            "center": {
                                "type": "geo_point"
                            },
                            "id": {
                                "type": "keyword"
                            },
                            "type": {
                                "type": "keyword"
                            },
                            "name": {
                                "type": "text",
                                "fields": {
                                    "keyword": {
                                        "type": "keyword",
                                        "ignore_above": 256
                                    }
                                }
                            },
                            "country": {
                                "properties": {
                                    "code": {
                                        "type": "keyword"
                                    },
                                    "name": {
                                        "type": "text"
                                    }
                                }
                            },
                            "hotels_number": {
                                "type": "integer"
                            }
                        }
                    }
                }
            )
            logger.info(f"Created index '{index_name}'")
        
        # Prepara e carica i documenti in batch
        doc_count = 0
        bulk_actions = []
        
        with open(input_path, 'r', encoding='utf-8') as file:
            for line in file:
                try:
                    doc = json.loads(line.strip())
                    
                    # Calcola il numero di hotel
                    hotels_number = len(doc.get('hotels', [])) if doc.get('hotels') else 0
                    
                    # Crea un documento pulito con i campi rilevanti
                    doc_cleaned = {
                        'center': doc.get('center'),
                        'hids': doc.get('hids'),
                        'hotels': doc.get('hotels'),
                        'hotels_number': hotels_number,
                        'id': doc.get('id'),
                        'type': doc.get('type'),
                        'country': doc.get('country'),
                        'name': doc.get('name', {}).get('en') or doc.get('name', {}).get('it')
                    }
                    
                    # Aggiungi l'azione di indicizzazione
                    bulk_actions.append({
                        "_index": index_name,
                        "_source": doc_cleaned
                    })
                    
                    doc_count += 1
                    
                    # Esegui l'upload in batch
                    if len(bulk_actions) >= batch_size:
                        helpers.bulk(client, bulk_actions)
                        logger.info(f"Loaded {doc_count} documents")
                        bulk_actions = []
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"Error parsing line: {e}")
                    continue
        
        # Carica eventuali documenti rimanenti
        if bulk_actions:
            helpers.bulk(client, bulk_actions)
            logger.info(f"Loaded final batch. Total: {doc_count} documents")
        
        # Aggiorna l'indice
        client.indices.refresh(index=index_name)
        
        # Chiudi la connessione
        client.close()
        
        logger.info(f"Completed loading {doc_count} documents to OpenSearch")
        return doc_count
        
    except Exception as e:
        logger.error(f"Error loading regions to OpenSearch: {str(e)}")
        raise SyncError(f"Error loading regions to OpenSearch: {str(e)}")


def sync_regions_to_opensearch(
    dump_url: str, 
    index_name: str = 'region_italy_ratehawk',
    opensearch_config: Optional[Dict[str, Any]] = None,
    data_dir: str = './data'
) -> Dict[str, Any]:
    """
    Esegue il processo completo di sincronizzazione:
    1. Scarica il dump delle regioni
    2. Decomprime il file
    3. Filtra per regioni italiane
    4. Carica in OpenSearch
    
    Args:
        dump_url: URL del file di dump
        index_name: Nome dell'indice OpenSearch
        opensearch_config: Configurazione OpenSearch
        data_dir: Directory per i file temporanei
        
    Returns:
        Dizionario con risultati della sincronizzazione
        
    Raises:
        SyncError: Se si verifica un errore durante il processo
    """
    if opensearch_config is None:
        opensearch_config = {
            'hosts': [{'host': 'localhost', 'port': 9200}],
            'auth': ('admin', 'admin'),
            'use_ssl': False,
            'verify_certs': False,
            'ssl_assert_hostname': False,
            'ssl_show_warn': False
        }
    
    os.makedirs(data_dir, exist_ok=True)
    
    # Definisci i percorsi dei file
    compressed_file = os.path.join(data_dir, 'region_dump.jsonl.zst')
    decompressed_file = os.path.join(data_dir, 'region_dump.jsonl')
    filtered_file = os.path.join(data_dir, 'region_italy.jsonl')
    
    try:
        # 1. Scarica il dump
        download_region_dump(dump_url, compressed_file)
        
        # 2. Decomprime il file
        decompress_zstd_file(compressed_file, decompressed_file)
        
        # 3. Filtra per regioni italiane
        filter_italian_regions(decompressed_file, filtered_file)
        
        # 4. Carica in OpenSearch
        doc_count = load_regions_to_opensearch(filtered_file, index_name, opensearch_config)
        
        # Restituisci i risultati
        return {
            'status': 'success',
            'documents_loaded': doc_count,
            'index_name': index_name,
            'filtered_file': filtered_file
        }
        
    except Exception as e:
        logger.error(f"Error in sync process: {str(e)}")
        raise SyncError(f"Error in region sync process: {str(e)}")