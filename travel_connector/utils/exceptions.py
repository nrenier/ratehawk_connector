"""
Custom exceptions for the travel connector package.
"""

class ConnectorError(Exception):
    """Base exception for all connector errors"""
    pass


class AdapterError(ConnectorError):
    """Exception raised for errors in the adapter classes"""
    pass


class TransformationError(ConnectorError):
    """Exception raised for errors in data transformation"""
    pass


class ValidationError(ConnectorError):
    """Exception raised for data validation errors"""
    pass


class ConfigurationError(ConnectorError):
    """Exception raised for configuration errors"""
    pass


class SyncError(ConnectorError):
    """Exception raised for errors during data synchronization"""
    pass
