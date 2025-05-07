# Travel Connector

A unified data model and connector system for normalizing and transforming heterogeneous travel industry API data.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![Pydantic](https://img.shields.io/badge/pydantic-2.5+-orange.svg)](https://pydantic-docs.helpmanual.io/)
[![OpenSearch](https://img.shields.io/badge/opensearch-2.3+-yellow.svg)](https://opensearch.org/)

## Overview

Travel Connector provides a standardized way to interact with various travel industry APIs through a single, consistent interface. It handles the complexity of different data formats and API structures, allowing developers to work with a uniform data model.

This connector currently supports Ratehawk/WorldOta API and can be extended to support additional travel data providers.

### Key Features

- **Standardized Data Model**: Unified representation of travel entities (hotels, rooms, bookings, etc.)
- **API Adapters**: Connect to multiple travel data sources through consistent interfaces
- **Data Transformation**: Convert between source-specific and standardized data formats
- **Extensible Architecture**: Easy to add support for new APIs and data sources
- **REST API**: Simple HTTP interface for accessing normalized travel data
- **OpenSearch Integration**: Efficient search capabilities for hotel and region data
- **Authentication Support**: Handles API key and basic authentication scenarios

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/travel-connector.git
cd travel-connector

# Create a virtual environment (optional)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies (see dependencies.md for details)
pip install -r requirements.txt
```

## Configuration

Create a `.env` file in the root directory with the following environment variables:

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

## API Endpoints

### Hotel Endpoints

- `GET /api/hotels/search` - Search for hotels based on location, dates, etc.
- `GET /api/hotels/region` - Search for hotels in a specific region
- `GET /api/hotels/name` - Search for hotels by name
- `GET /api/hotels/{hotel_id}` - Get details for a specific hotel
- `GET /api/hotels/{hotel_id}/rooms` - Get available rooms for a specific hotel
- `POST /api/hotels/sync` - Synchronize hotel data from API to OpenSearch

### Region Endpoints

- `GET /api/regions/province` - Search for regions by province name
- `GET /api/regions/dump` - Get complete region data dump
- `POST /api/regions/sync` - Synchronize region data from API to OpenSearch

### Booking Endpoints

- `POST /api/bookings` - Create a new booking
- `GET /api/bookings/{booking_id}` - Get details of a specific booking
- `DELETE /api/bookings/{booking_id}` - Cancel a booking

### System Endpoints

- `GET /api/opensearch/status` - Check OpenSearch connection status
- `GET /` - Home page (API documentation)

## Architecture

The connector follows a layered architecture:

1. **API Layer**: Flask routes that expose REST endpoints
2. **Connector Layer**: The main TravelConnector class that coordinates between adapters
3. **Adapter Layer**: Adapters for specific APIs (e.g., RatehawkAdapter)
4. **Transformer Layer**: Converters between source-specific and standardized data formats
5. **Model Layer**: Pydantic models representing standardized data entities
6. **Utility Layer**: Helper tools for tasks like synchronization and search

## Authentication

The connector supports both API key and Basic Auth authentication methods:

- **API Key**: Used in headers as `X-API-KEY` for some endpoints
- **Basic Auth**: Used with KEY_ID and API_KEY for certain endpoints like data dumps

The `RATEHAWK_KEY_ID` is typically set to `5412` as per the official documentation.

## OpenSearch Integration

The connector uses OpenSearch for efficient storage and querying of hotel and region data:

1. **Region Synchronization**: Regions are downloaded, filtered for Italian regions, and stored in OpenSearch
2. **Hotel Synchronization**: Hotels are downloaded, filtered for Italian hotels, and stored in OpenSearch
3. **Search Optimization**: Searches first attempt to use OpenSearch for better performance, with fallback to direct API calls

To check OpenSearch connection status, use the `/api/opensearch/status` endpoint.

## Development

### Adding a New API Provider

To add support for a new travel API:

1. Create a new adapter in `travel_connector/adapters/`
2. Create a new transformer in `travel_connector/transformers/`
3. Update the `TravelConnector` class to register and use the new adapter
4. Add configuration parameters to the `.env` file

### Testing

Run tests using pytest:

```bash
pytest tests/
```

### Code Structure

```
travel_connector/
├── adapters/              # API-specific adapters
│   ├── base_adapter.py    # Base adapter interface
│   └── ratehawk_adapter.py # Ratehawk implementation
├── models/                # Standardized data models
│   ├── base.py            # Base model classes
│   ├── hotel.py           # Hotel model
│   ├── room.py            # Room model
│   └── booking.py         # Booking model
├── transformers/          # Data transformers
│   ├── base_transformer.py # Base transformer interface
│   └── ratehawk_transformer.py # Ratehawk implementation
├── utils/                 # Utility functions
│   ├── region_sync.py     # Region synchronization
│   ├── hotel_sync.py      # Hotel synchronization  
│   └── opensearch_client.py # OpenSearch client
├── config.py              # Configuration management
└── main.py                # Main connector class
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.
