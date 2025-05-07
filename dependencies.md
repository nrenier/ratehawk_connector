# Project Dependencies

## Core Dependencies
- flask==2.3.3
- flask-login==0.6.2
- flask-sqlalchemy==3.1.1
- gunicorn==23.0.0
- python-dotenv==1.0.0
- sqlalchemy==2.0.23
- Werkzeug==2.3.7

## Database
- psycopg2-binary==2.9.9

## Travel API Libraries
- requests==2.31.0
- pydantic==2.5.2
- email-validator==2.1.0

## OpenSearch
- opensearch-py==2.3.2

## File Handling
- zstandard==0.22.0
- trafilatura==1.6.3

## Testing
- pytest==7.4.3
- responses==0.24.1

## Installation in standard Python environment

```shell
pip install -r requirements.txt
```

## Environment Variables Required

Make sure to have these environment variables set in your .env file:

```
# Configurazione API Ratehawk
RATEHAWK_URL=https://api.worldota.net/api/
RATEHAWK_API_KEY=your_api_key_here
RATEHAWK_KEY_ID=5412

# Configurazione OpenSearch
OPENSEARCH_HOST=localhost
OPENSEARCH_PORT=9200
OPENSEARCH_USER=admin
OPENSEARCH_PASSWORD=admin
OPENSEARCH_USE_SSL=false
OPENSEARCH_VERIFY_CERTS=false

# Configurazione Flask
SESSION_SECRET=your_secret_key_here
```