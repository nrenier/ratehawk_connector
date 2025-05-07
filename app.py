import os
import logging

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix

from travel_connector.main import create_connector
from travel_connector.utils.exceptions import ConnectorError

# Configure logging
logging.basicConfig(level=logging.DEBUG,
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)
# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# configure the database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
# initialize the app with the extension, flask-sqlalchemy >= 3.0.x
db.init_app(app)

# Create the travel connector
try:
    travel_connector = create_connector()
    logger.info("Travel connector initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize travel connector: {str(e)}")
    travel_connector = None


with app.app_context():
    # Make sure to import the models here or their tables won't be created
    import models  # noqa: F401

    db.create_all()


@app.route('/')
def home():
    """Home page route"""
    return jsonify({
        "status": "ok",
        "message": "Travel connector API is running"
    })


@app.route('/api/hotels/search', methods=['POST'])
def search_hotels():
    """API endpoint to search for hotels"""
    if not travel_connector:
        return jsonify({
            "status": "error",
            "message": "Travel connector not initialized"
        }), 500
    
    try:
        data = request.json
        source = data.get('source', 'ratehawk')
        search_params = data.get('params', {})
        
        hotels = travel_connector.search_hotels(source, search_params)
        
        return jsonify({
            "status": "success",
            "data": {
                "hotels": [hotel.dict(exclude={'raw_data'}) for hotel in hotels]
            }
        })
    except ConnectorError as e:
        logger.error(f"Error searching hotels: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error searching hotels: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred"
        }), 500


@app.route('/api/hotels/<hotel_id>', methods=['GET'])
def get_hotel_details(hotel_id):
    """API endpoint to get hotel details"""
    if not travel_connector:
        return jsonify({
            "status": "error",
            "message": "Travel connector not initialized"
        }), 500
    
    try:
        source = request.args.get('source', 'ratehawk')
        
        hotel = travel_connector.get_hotel_details(source, hotel_id)
        
        return jsonify({
            "status": "success",
            "data": {
                "hotel": hotel.dict(exclude={'raw_data'})
            }
        })
    except ConnectorError as e:
        logger.error(f"Error getting hotel details: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error getting hotel details: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred"
        }), 500


@app.route('/api/hotels/<hotel_id>/rooms', methods=['POST'])
def search_rooms(hotel_id):
    """API endpoint to search for rooms"""
    if not travel_connector:
        return jsonify({
            "status": "error",
            "message": "Travel connector not initialized"
        }), 500
    
    try:
        data = request.json
        source = data.get('source', 'ratehawk')
        search_params = data.get('params', {})
        
        rooms = travel_connector.search_rooms(source, hotel_id, search_params)
        
        return jsonify({
            "status": "success",
            "data": {
                "rooms": [room.dict(exclude={'raw_data'}) for room in rooms]
            }
        })
    except ConnectorError as e:
        logger.error(f"Error searching rooms: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error searching rooms: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred"
        }), 500


@app.route('/api/bookings', methods=['POST'])
def create_booking():
    """API endpoint to create a booking"""
    if not travel_connector:
        return jsonify({
            "status": "error",
            "message": "Travel connector not initialized"
        }), 500
    
    try:
        data = request.json
        source = data.get('source', 'ratehawk')
        booking_data = data.get('booking', {})
        
        booking = travel_connector.create_booking(source, booking_data)
        
        return jsonify({
            "status": "success",
            "data": {
                "booking": booking.dict(exclude={'raw_data'})
            }
        })
    except ConnectorError as e:
        logger.error(f"Error creating booking: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error creating booking: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred"
        }), 500


@app.route('/api/bookings/<booking_id>', methods=['GET'])
def get_booking(booking_id):
    """API endpoint to get booking details"""
    if not travel_connector:
        return jsonify({
            "status": "error",
            "message": "Travel connector not initialized"
        }), 500
    
    try:
        source = request.args.get('source', 'ratehawk')
        
        booking = travel_connector.get_booking(source, booking_id)
        
        return jsonify({
            "status": "success",
            "data": {
                "booking": booking.dict(exclude={'raw_data'})
            }
        })
    except ConnectorError as e:
        logger.error(f"Error getting booking details: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error getting booking details: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred"
        }), 500


@app.route('/api/bookings/<booking_id>', methods=['DELETE'])
def cancel_booking(booking_id):
    """API endpoint to cancel a booking"""
    if not travel_connector:
        return jsonify({
            "status": "error",
            "message": "Travel connector not initialized"
        }), 500
    
    try:
        source = request.args.get('source', 'ratehawk')
        
        booking = travel_connector.cancel_booking(source, booking_id)
        
        return jsonify({
            "status": "success",
            "data": {
                "booking": booking.dict(exclude={'raw_data'})
            }
        })
    except ConnectorError as e:
        logger.error(f"Error cancelling booking: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Unexpected error cancelling booking: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "An unexpected error occurred"
        }), 500


@app.route('/api/hotels/dump', methods=['GET'])
def get_hotel_dump():
    """
    API endpoint per recuperare il dump statico completo degli hotel
    
    Questa funzione sincronizzata recupera tutti i dati sugli hotel disponibili nell'API.
    È possibile utilizzare parametri di query per filtrare i risultati.
    
    Query Parameters:
        source (str): Nome del fornitore da utilizzare (default: 'ratehawk')
        hotel_ids (list): Lista di ID hotel specifici da recuperare
        city_ids (list): Lista di ID città per filtrare gli hotel per località
        modified_after (str): Timestamp per recuperare solo gli hotel modificati dopo questa data
        language (str): Codice lingua (es. "it", "en", "fr")
    
    Returns:
        JSON contenente il dump degli hotel
    """
    if not travel_connector:
        return jsonify({
            "status": "error",
            "message": "Travel connector not initialized"
        }), 500
    
    try:
        source = request.args.get('source', 'ratehawk')
        
        # Raccoglie i parametri dalla richiesta
        params = {}
        for key, value in request.args.items():
            if key != 'source':
                params[key] = value
        
        # Gestione speciale per parametri che dovrebbero essere liste
        for list_param in ['hotel_ids', 'city_ids']:
            if list_param in params and isinstance(params[list_param], str):
                # Converte le stringhe separate da virgole in liste
                params[list_param] = [item.strip() for item in params[list_param].split(',')]
        
        # Recupera il dump degli hotel
        dump_data = travel_connector.get_hotel_dump(source, params)
        
        # Conteggia il totale degli elementi nel dump se non già presente
        if 'total' not in dump_data and 'items' in dump_data:
            dump_data['total'] = len(dump_data['items'])
        
        return jsonify({
            "status": "success",
            "data": dump_data
        })
    except ConnectorError as e:
        logger.error(f"Errore nel recupero del dump degli hotel: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Errore imprevisto nel recupero del dump degli hotel: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Si è verificato un errore imprevisto"
        }), 500


@app.route('/api/hotels/incremental-dump', methods=['GET'])
def get_hotel_incremental_dump():
    """
    API endpoint per recuperare il dump incrementale degli hotel
    
    Questa funzione sincronizzata recupera le modifiche agli hotel rispetto al giorno precedente
    o in base all'intervallo specificato. È possibile utilizzare parametri di query per filtrare i risultati.
    
    Query Parameters:
        source (str): Nome del fornitore da utilizzare (default: 'ratehawk')
        hotel_ids (list): Lista di ID hotel specifici da recuperare
        city_ids (list): Lista di ID città per filtrare gli hotel per località
        from_date (str): Data di inizio per il filtro (formato ISO: YYYY-MM-DD)
        to_date (str): Data di fine per il filtro (formato ISO: YYYY-MM-DD)
        language (str): Codice lingua (es. "it", "en", "fr")
    
    Returns:
        JSON contenente il dump incrementale degli hotel
    """
    if not travel_connector:
        return jsonify({
            "status": "error",
            "message": "Travel connector not initialized"
        }), 500
    
    try:
        source = request.args.get('source', 'ratehawk')
        
        # Raccoglie i parametri dalla richiesta
        params = {}
        for key, value in request.args.items():
            if key != 'source':
                params[key] = value
        
        # Gestione speciale per parametri che dovrebbero essere liste
        for list_param in ['hotel_ids', 'city_ids']:
            if list_param in params and isinstance(params[list_param], str):
                # Converte le stringhe separate da virgole in liste
                params[list_param] = [item.strip() for item in params[list_param].split(',')]
        
        # Recupera il dump incrementale degli hotel
        dump_data = travel_connector.get_hotel_incremental_dump(source, params)
        
        # Conteggia il totale degli elementi nel dump se non già presente
        if 'total' not in dump_data and 'items' in dump_data:
            dump_data['total'] = len(dump_data['items'])
        
        return jsonify({
            "status": "success",
            "data": dump_data
        })
    except ConnectorError as e:
        logger.error(f"Errore nel recupero del dump incrementale degli hotel: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Errore imprevisto nel recupero del dump incrementale degli hotel: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Si è verificato un errore imprevisto"
        }), 500


@app.route('/api/hotels/region', methods=['GET'])
def search_hotels_by_region():
    """
    API endpoint per cercare hotel in base alla regione specificata
    
    Questa funzione consente di cercare hotel in una regione geografica specifica,
    come un paese, una città o un'area particolare.
    
    Query Parameters:
        source (str): Nome del fornitore da utilizzare (default: 'ratehawk')
        region_id (str, obbligatorio): ID della regione da ricercare
        language (str): Codice lingua (es. "it", "en", "fr")
        currency (str): Codice valuta (es. "EUR", "USD")
        hotels_count (int): Numero massimo di hotel da restituire
        page (int): Numero di pagina per la paginazione dei risultati
        residency (str): Paese di residenza del cliente (codice ISO)
        checkin (str): Data di check-in (formato ISO: YYYY-MM-DD)
        checkout (str): Data di check-out (formato ISO: YYYY-MM-DD)
        adults (int): Numero di adulti
        children (list): Lista di età dei bambini
        guest_name (str): Nome del cliente
    
    Returns:
        JSON contenente i risultati della ricerca per regione
    """
    if not travel_connector:
        return jsonify({
            "status": "error",
            "message": "Travel connector not initialized"
        }), 500
    
    try:
        source = request.args.get('source', 'ratehawk')
        
        # Verifica la presenza dei parametri obbligatori
        if 'region_id' not in request.args:
            return jsonify({
                "status": "error",
                "message": "Il parametro 'region_id' è obbligatorio per la ricerca per regione"
            }), 400
        
        # Raccoglie i parametri dalla richiesta
        params = {}
        for key, value in request.args.items():
            if key != 'source':
                params[key] = value
        
        # Gestione speciale per i parametri numerici
        for num_param in ['hotels_count', 'page', 'adults']:
            if num_param in params and isinstance(params[num_param], str):
                try:
                    params[num_param] = int(params[num_param])
                except ValueError:
                    pass  # Mantiene il valore come stringa se non è convertibile
        
        # Gestione speciale per parametri che dovrebbero essere liste
        if 'children' in params and isinstance(params['children'], str):
            try:
                # Tenta di convertire le età dei bambini in una lista di interi
                params['children'] = [int(age.strip()) for age in params['children'].split(',')]
            except ValueError:
                pass  # Mantiene il valore come stringa se non è convertibile
        
        # Ottieni il parametro per OpenSearch dalla richiesta
        use_opensearch = request.args.get('use_opensearch', 'true').lower() == 'true'
        
        # Cerca hotel in base alla regione, con opzione per OpenSearch
        search_results = travel_connector.search_hotels_by_region(source, params, use_opensearch)
        
        return jsonify({
            "status": "success",
            "data": search_results
        })
    except ValueError as e:
        logger.error(f"Errore nei parametri di ricerca: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except ConnectorError as e:
        logger.error(f"Errore nella ricerca di hotel per regione: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Errore imprevisto nella ricerca di hotel per regione: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Si è verificato un errore imprevisto"
        }), 500


@app.route('/api/regions/dump', methods=['GET'])
def get_region_dump():
    """
    API endpoint per recuperare il dump completo delle regioni
    
    Questa funzione sincronizzata restituisce tutti i dati sulle regioni disponibili nell'API.
    È possibile utilizzare parametri di query per filtrare i risultati.
    
    Query Parameters:
        source (str): Nome del fornitore da utilizzare (default: 'ratehawk')
        ids (list): Lista di ID regioni specifici da recuperare
        language (str): Codice lingua (es. "it", "en", "fr")
    
    Returns:
        JSON contenente il dump completo delle regioni
    """
    if not travel_connector:
        return jsonify({
            "status": "error",
            "message": "Travel connector not initialized"
        }), 500
    
    try:
        source = request.args.get('source', 'ratehawk')
        
        # Raccoglie i parametri dalla richiesta
        params = {}
        for key, value in request.args.items():
            if key != 'source':
                params[key] = value
        
        # Gestione speciale per parametri che dovrebbero essere liste
        if 'ids' in params and isinstance(params['ids'], str):
            # Converte le stringhe separate da virgole in liste
            params['ids'] = [item.strip() for item in params['ids'].split(',')]
        
        # Recupera il dump delle regioni
        dump_data = travel_connector.get_region_dump(source, params)
        
        # Conteggia il totale degli elementi nel dump se non già presente
        if 'total' not in dump_data and 'items' in dump_data:
            dump_data['total'] = len(dump_data['items'])
        
        return jsonify({
            "status": "success",
            "data": dump_data
        })
    except ConnectorError as e:
        logger.error(f"Errore nel recupero del dump delle regioni: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Errore imprevisto nel recupero del dump delle regioni: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Si è verificato un errore imprevisto"
        }), 500


@app.route('/api/regions/province', methods=['GET'])
def search_region_by_province():
    """
    API endpoint per cercare il region_id in base ad una provincia specificata
    
    Questa funzione consente di trovare l'identificativo di una regione (region_id) 
    cercando per nome di provincia. Utile per ottenere il region_id da utilizzare 
    nell'endpoint /api/hotels/region.
    
    Query Parameters:
        source (str): Nome del fornitore da utilizzare (default: 'ratehawk')
        province (str, obbligatorio): Nome della provincia da cercare
        language (str): Codice lingua (default: 'it')
    
    Returns:
        JSON contenente la lista di regioni trovate che corrispondono alla provincia
    """
    if not travel_connector:
        return jsonify({
            "status": "error",
            "message": "Travel connector not initialized"
        }), 500
    
    try:
        source = request.args.get('source', 'ratehawk')
        
        # Verifica la presenza dei parametri obbligatori
        if 'province' not in request.args:
            return jsonify({
                "status": "error",
                "message": "Il parametro 'province' è obbligatorio per la ricerca"
            }), 400
        
        province_name = request.args.get('province')
        language = request.args.get('language', 'it')
        
        # Controlla se usare OpenSearch (default: True)
        use_opensearch_str = request.args.get('use_opensearch', 'true')
        use_opensearch = use_opensearch_str.lower() in ['true', '1', 'yes']
        
        # Cerca regioni in base alla provincia
        regions = travel_connector.search_region_by_province(source, province_name, language, use_opensearch)
        
        # Aggiunge suggerimenti sulla modalità di utilizzo dei risultati
        usage_tip = "Per utilizzare questi risultati, seleziona l'ID della regione desiderata e utilizzalo come 'region_id' nell'endpoint /api/hotels/region"
        
        return jsonify({
            "status": "success",
            "usage_tip": usage_tip,
            "data": regions
        })
    except ConnectorError as e:
        logger.error(f"Errore nella ricerca di regioni per provincia: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Errore imprevisto nella ricerca di regioni per provincia: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Si è verificato un errore imprevisto"
        }), 500


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        "status": "error",
        "message": "Resource not found"
    }), 404


@app.route('/api/regions/sync', methods=['POST'])
def sync_regions():
    """
    API endpoint per sincronizzare le regioni da Ratehawk a OpenSearch
    
    Questo endpoint avvia il processo di sincronizzazione che:
    1. Scarica il dump completo delle regioni
    2. Decomprime il file
    3. Filtra per regioni italiane (country_code: IT)
    4. Carica i dati in OpenSearch
    
    JSON Body Parameters:
        index_name (str, opzionale): Nome dell'indice OpenSearch (default: 'region_italy_ratehawk')
        opensearch_config (dict, opzionale): Configurazione personalizzata per OpenSearch
    
    Returns:
        JSON con risultati della sincronizzazione
    """
    if not travel_connector:
        return jsonify({
            "status": "error",
            "message": "Travel connector not initialized"
        }), 500
    
    try:
        # Ottieni i parametri dal corpo JSON
        data = request.json or {}
        index_name = data.get('index_name', 'region_italy_ratehawk')
        opensearch_config = data.get('opensearch_config')
        
        # Importa la funzionalità di sincronizzazione
        from travel_connector.utils.region_sync import sync_regions_to_opensearch
        
        # Recupera l'URL del dump più recente
        dump_response = travel_connector.get_region_dump("ratehawk", {"language": "it"})
        dump_url = dump_response.get("data", {}).get("url")
        
        if not dump_url:
            return jsonify({
                "status": "error",
                "message": "Impossibile ottenere l'URL del dump delle regioni"
            }), 400
        
        # Configura OpenSearch dai parametri o dalle variabili di ambiente
        if not opensearch_config:
            opensearch_config = {
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
        
        # Esegui la sincronizzazione (avvia in un thread in background)
        import threading
        
        def sync_task():
            try:
                sync_regions_to_opensearch(
                    dump_url=dump_url,
                    index_name=index_name,
                    opensearch_config=opensearch_config,
                    data_dir="./data"
                )
                logger.info(f"Sincronizzazione completata per l'indice {index_name}")
            except Exception as e:
                logger.error(f"Errore nella sincronizzazione: {str(e)}")
        
        thread = threading.Thread(target=sync_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "success",
            "message": "Sincronizzazione avviata in background",
            "dump_url": dump_url,
            "index_name": index_name
        })
        
    except Exception as e:
        logger.error(f"Errore nell'avvio della sincronizzazione: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Errore nell'avvio della sincronizzazione: {str(e)}"
        }), 500


@app.route('/api/hotels/name', methods=['GET'])
def search_hotels_by_name():
    """
    API endpoint per cercare hotel in base al nome specificato
    
    Questa funzione consente di trovare hotel cercando per nome. La ricerca è ottimizzata
    per trovare corrispondenze anche parziali.
    
    Query Parameters:
        source (str): Nome del fornitore da utilizzare (default: 'ratehawk')
        name (str, obbligatorio): Nome dell'hotel da cercare
        language (str): Codice lingua (default: 'it')
        use_opensearch (bool): Se utilizzare OpenSearch quando disponibile (default: true)
        
    Returns:
        JSON contenente la lista di hotel trovati che corrispondono al nome
    """
    if not travel_connector:
        return jsonify({
            "status": "error",
            "message": "Travel connector not initialized"
        }), 500
    
    try:
        source = request.args.get('source', 'ratehawk')
        
        # Verifica la presenza dei parametri obbligatori
        if 'name' not in request.args:
            return jsonify({
                "status": "error",
                "message": "Il parametro 'name' è obbligatorio per la ricerca"
            }), 400
        
        hotel_name = request.args.get('name')
        language = request.args.get('language', 'it')
        
        # Controlla se usare OpenSearch (default: True)
        use_opensearch_str = request.args.get('use_opensearch', 'true')
        use_opensearch = use_opensearch_str.lower() in ['true', '1', 'yes']
        
        # Cerca hotel in base al nome
        hotels = travel_connector.search_hotels_by_name(source, hotel_name, language, use_opensearch)
        
        return jsonify({
            "status": "success",
            "data": hotels
        })
    except ConnectorError as e:
        logger.error(f"Errore nella ricerca di hotel per nome: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 400
    except Exception as e:
        logger.error(f"Errore imprevisto nella ricerca di hotel per nome: {str(e)}")
        return jsonify({
            "status": "error",
            "message": "Si è verificato un errore imprevisto"
        }), 500


@app.route('/api/hotels/sync', methods=['POST'])
def sync_hotels():
    """
    API endpoint per sincronizzare gli hotel da Ratehawk a OpenSearch
    
    Questo endpoint avvia il processo di sincronizzazione che:
    1. Scarica il dump completo degli hotel
    2. Decomprime il file
    3. Filtra per hotel italiani (country_code: IT)
    4. Carica i dati in OpenSearch
    
    JSON Body Parameters:
        index_name (str, opzionale): Nome dell'indice OpenSearch (default: 'hotel_ratehawk')
        country_code (str, opzionale): Codice del paese per filtrare gli hotel (default: 'IT')
        opensearch_config (dict, opzionale): Configurazione personalizzata per OpenSearch
    
    Returns:
        JSON con risultati della sincronizzazione
    """
    if not travel_connector:
        return jsonify({
            "status": "error",
            "message": "Travel connector not initialized"
        }), 500
    
    try:
        # Ottieni i parametri dal corpo JSON
        data = request.json or {}
        index_name = data.get('index_name', 'hotel_ratehawk')
        country_code = data.get('country_code', 'IT')
        opensearch_config = data.get('opensearch_config')
        
        # Importa la funzionalità di sincronizzazione
        from travel_connector.utils.hotel_sync import sync_hotels_from_ratehawk
        
        # Ottieni l'adapter per Ratehawk
        adapter = travel_connector.get_adapter("ratehawk")
        
        # Configura OpenSearch dai parametri o dalle variabili di ambiente
        if not opensearch_config:
            opensearch_config = {
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
        
        # Esegui la sincronizzazione (avvia in un thread in background)
        import threading
        
        def sync_task():
            try:
                sync_result = sync_hotels_from_ratehawk(adapter, country_code=country_code)
                status = "success" if sync_result else "error"
                logger.info(f"Sincronizzazione degli hotel completata: {status}")
            except Exception as e:
                logger.error(f"Errore nella sincronizzazione degli hotel: {str(e)}")
        
        thread = threading.Thread(target=sync_task)
        thread.daemon = True
        thread.start()
        
        return jsonify({
            "status": "success",
            "message": "Sincronizzazione degli hotel avviata in background",
            "index_name": index_name,
            "country_code": country_code
        })
        
    except Exception as e:
        logger.error(f"Errore nell'avvio della sincronizzazione degli hotel: {str(e)}")
        return jsonify({
            "status": "error",
            "message": f"Errore nell'avvio della sincronizzazione: {str(e)}"
        }), 500


@app.route('/api/opensearch/status', methods=['GET'])
def check_opensearch_status():
    """
    API endpoint per verificare lo stato della connessione a OpenSearch
    
    Questo endpoint verifica se il servizio OpenSearch è accessibile e 
    restituisce informazioni sulla versione e sulla disponibilità.
    
    Query Parameters:
        host (str, opzionale): Host del server OpenSearch
        port (int, opzionale): Porta del server OpenSearch
        
    Returns:
        JSON con lo stato della connessione OpenSearch
    """
    try:
        # Importa il client OpenSearch
        from travel_connector.utils.opensearch_client import check_opensearch_connection
        
        # Crea la configurazione utilizzando i parametri o le variabili di ambiente
        config = {
            'hosts': [{
                'host': request.args.get('host', os.environ.get('OPENSEARCH_HOST', 'localhost')),
                'port': int(request.args.get('port', os.environ.get('OPENSEARCH_PORT', 9200)))
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
        
        # Verifica la connessione
        status = check_opensearch_connection(config)
        
        # Aggiunge informazioni sulla configurazione
        status['config'] = {
            'host': config['hosts'][0]['host'],
            'port': config['hosts'][0]['port'],
            'use_ssl': config['use_ssl']
        }
        
        return jsonify({
            "status": "success",
            "data": status
        })
        
    except Exception as e:
        logger.error(f"Errore nel controllo della connessione OpenSearch: {str(e)}")
        return jsonify({
            "status": "error",
            "message": str(e)
        }), 500


@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    return jsonify({
        "status": "error",
        "message": "Internal server error"
    }), 500
