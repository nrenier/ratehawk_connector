#!/usr/bin/env python
"""
Script di utility per sincronizzare le regioni da Ratehawk a OpenSearch.

Questo script può essere eseguito manualmente per aggiornare i dati delle regioni.
Recupera l'URL del dump più recente, scarica il file, decomprime, filtra per regioni italiane
e carica i dati in OpenSearch.

Utilizzo:
    python sync_regions.py

Per personalizzare la configurazione, utilizzare le variabili di ambiente:
    - OPENSEARCH_HOST: host del server OpenSearch (default: localhost)
    - OPENSEARCH_PORT: porta del server OpenSearch (default: 9200)
    - OPENSEARCH_USER: username per OpenSearch (default: admin)
    - OPENSEARCH_PASSWORD: password per OpenSearch (default: admin)
    - OPENSEARCH_INDEX: nome dell'indice per le regioni (default: region_italy_ratehawk)
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, Any

from travel_connector.main import create_connector
from travel_connector.utils.exceptions import ConnectorError, SyncError
from travel_connector.utils.region_sync import sync_regions_to_opensearch

# Configurazione del logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_region_dump_url() -> str:
    """
    Ottiene l'URL del dump delle regioni più recente da Ratehawk
    
    Returns:
        URL del file di dump
        
    Raises:
        ConnectorError: Se non è possibile ottenere l'URL
    """
    try:
        # Ottieni RATEHAWK_URL dall'ambiente
        import os
        ratehawk_url = os.environ.get('RATEHAWK_URL')
        
        # Crea un'istanza del connector con l'URL corretto
        connector = create_connector()
        
        # Recupera il dump delle regioni (solo i metadati, non il file completo)
        response = connector.get_region_dump("ratehawk", {"language": "it"})
        
        # Estrai l'URL del file
        dump_url = response.get("data", {}).get("url")
        if not dump_url:
            raise ConnectorError("URL del dump non trovato nella risposta dell'API")
        
        return dump_url
        
    except Exception as e:
        logger.error(f"Errore nel recupero dell'URL del dump: {str(e)}")
        raise ConnectorError(f"Errore nel recupero dell'URL del dump: {str(e)}")


def get_opensearch_config() -> Dict[str, Any]:
    """
    Costruisce la configurazione OpenSearch dalle variabili di ambiente
    
    Returns:
        Configurazione OpenSearch
    """
    return {
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


def main():
    """Funzione principale dello script"""
    parser = argparse.ArgumentParser(description="Sincronizza le regioni da Ratehawk a OpenSearch")
    parser.add_argument("--index", help="Nome dell'indice OpenSearch", default=os.environ.get('OPENSEARCH_INDEX', 'region_italy_ratehawk'))
    parser.add_argument("--data-dir", help="Directory per i file temporanei", default="./data")
    parser.add_argument("--url", help="URL diretto del dump (opzionale, altrimenti viene recuperato da Ratehawk)")
    
    args = parser.parse_args()
    
    try:
        # Recupera l'URL del dump
        if args.url:
            dump_url = args.url
            logger.info(f"Utilizzo URL fornito: {dump_url}")
        else:
            dump_url = get_region_dump_url()
            logger.info(f"URL del dump recuperato: {dump_url}")
        
        # Ottieni la configurazione OpenSearch
        opensearch_config = get_opensearch_config()
        
        # Esegui la sincronizzazione
        result = sync_regions_to_opensearch(
            dump_url=dump_url,
            index_name=args.index,
            opensearch_config=opensearch_config,
            data_dir=args.data_dir
        )
        
        logger.info(f"Sincronizzazione completata con successo: {json.dumps(result, indent=2)}")
        return 0
        
    except (ConnectorError, SyncError) as e:
        logger.error(f"Errore durante la sincronizzazione: {str(e)}")
        return 1
    except Exception as e:
        logger.error(f"Errore imprevisto: {str(e)}")
        return 2


if __name__ == "__main__":
    sys.exit(main())