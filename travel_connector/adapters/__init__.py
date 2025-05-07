"""
Adapters package containing API connectors for different travel data sources.
"""

from travel_connector.adapters.base_adapter import BaseAdapter
from travel_connector.adapters.ratehawk_adapter import RatehawkAdapter

__all__ = [
    'BaseAdapter',
    'RatehawkAdapter'
]
