"""
Script per sincronizzare gli hotel dall'API Ratehawk a OpenSearch.

Questo script esegue le seguenti operazioni:
1. Ottiene il dump completo degli hotel da Ratehawk
2. Scarica e decomprime il file JSONL.zst
3. Filtra gli hotel per paese (default: Italia)
4. Carica i dati filtrati in OpenSearch per ricerche efficienti

Per eseguire lo script:
python sync_hotels.py [--country IT]
"""

import os
import logging
import argparse
from dotenv import load_dotenv

from travel_connector.adapters.ratehawk_adapter import RatehawkAdapter
from travel_connector.utils.hotel_sync import sync_hotels_from_ratehawk, check_opensearch_status

# Carica le variabili d'ambiente
load_dotenv()

# Configurazione del logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger(__name__)

def main():
    """Funzione principale per la sincronizzazione degli hotel"""
    parser = argparse.ArgumentParser(description='Sincronizza gli hotel Ratehawk in OpenSearch')
    parser.add_argument('--country', type=str, default='IT', help='Codice del paese (default: IT per Italia)')
    args = parser.parse_args()
    
    # Verifica lo stato di OpenSearch
    status = check_opensearch_status()
    if not status["connected"]:
        logger.error("Impossibile connettersi a OpenSearch. Verifica che il servizio sia in esecuzione.")
        exit(1)
    
    logger.info(f"Connessione a OpenSearch stabilita. Stato cluster: {status.get('status')}")
    
    # Ottieni le credenziali Ratehawk dall'ambiente
    api_key = os.environ.get('RATEHAWK_API_KEY')
    ratehawk_url = os.environ.get('RATEHAWK_URL')
    
    if not api_key:
        logger.error("Credenziali Ratehawk non trovate. Imposta la variabile d'ambiente RATEHAWK_API_KEY.")
        exit(1)
    
    # Inizializza l'adapter Ratehawk con l'URL da .env
    adapter = RatehawkAdapter(api_key=api_key, api_url=ratehawk_url)
    
    # Esegui la sincronizzazione degli hotel
    if sync_hotels_from_ratehawk(adapter, country_code=args.country):
        logger.info("Sincronizzazione degli hotel completata con successo!")
        
        # Verifica lo stato finale di OpenSearch
        final_status = check_opensearch_status()
        logger.info(f"Hotel sincronizzati: {final_status.get('hotel_count', 0)}")
    else:
        logger.error("Sincronizzazione degli hotel fallita.")
        exit(1)

if __name__ == "__main__":
    main()