"""
Configuration for the travel connector package.
"""

import os
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    "apis": {
        "ratehawk": {
            "api_url": os.getenv("RATEHAWK_URL", "https://api.worldota.net/api/"),
            "timeout": 30,
        }
    },
    "adapter_settings": {
        "cache_enabled": False,
        "cache_ttl": 300,  # 5 minutes
        "retry_attempts": 3,
        "retry_delay": 1,  # seconds
    },
    "logging": {
        "level": "DEBUG",
        "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    }
}


def get_config() -> Dict[str, Any]:
    """
    Get the configuration for the travel connector
    
    Returns:
        Dictionary containing configuration values
    """
    config = DEFAULT_CONFIG.copy()
    
    # Override with environment variables if they exist
    apis_config = config["apis"]
    
    # Ratehawk API configuration
    # Prioritize RATEHAWK_URL
    ratehawk_url = os.getenv("RATEHAWK_URL")
    if ratehawk_url:
        apis_config["ratehawk"]["api_url"] = ratehawk_url
    elif os.getenv("RATEHAWK_API_URL"):
        apis_config["ratehawk"]["api_url"] = os.getenv("RATEHAWK_API_URL")
    
    if os.getenv("RATEHAWK_TIMEOUT"):
        try:
            apis_config["ratehawk"]["timeout"] = int(os.getenv("RATEHAWK_TIMEOUT"))
        except (ValueError, TypeError):
            logger.warning("Invalid RATEHAWK_TIMEOUT value, using default")
    
    # Adapter settings configuration
    adapter_settings = config["adapter_settings"]
    
    if os.getenv("CACHE_ENABLED") and os.getenv("CACHE_ENABLED").lower() in ["true", "1", "yes"]:
        adapter_settings["cache_enabled"] = True
    
    if os.getenv("CACHE_TTL"):
        try:
            adapter_settings["cache_ttl"] = int(os.getenv("CACHE_TTL"))
        except (ValueError, TypeError):
            logger.warning("Invalid CACHE_TTL value, using default")
    
    if os.getenv("RETRY_ATTEMPTS"):
        try:
            adapter_settings["retry_attempts"] = int(os.getenv("RETRY_ATTEMPTS"))
        except (ValueError, TypeError):
            logger.warning("Invalid RETRY_ATTEMPTS value, using default")
    
    if os.getenv("RETRY_DELAY"):
        try:
            adapter_settings["retry_delay"] = float(os.getenv("RETRY_DELAY"))
        except (ValueError, TypeError):
            logger.warning("Invalid RETRY_DELAY value, using default")
    
    # Logging configuration
    logging_config = config["logging"]
    
    if os.getenv("LOG_LEVEL"):
        logging_config["level"] = os.getenv("LOG_LEVEL")
    
    if os.getenv("LOG_FORMAT"):
        logging_config["format"] = os.getenv("LOG_FORMAT")
    
    return config


def get_api_key(api_name: str) -> str:
    """
    Get the API key for a specific API from environment variables
    
    Args:
        api_name: Name of the API (e.g., "ratehawk")
        
    Returns:
        API key from environment variables
        
    Raises:
        ValueError: If the API key is not configured
    """
    env_var_name = f"{api_name.upper()}_API_KEY"
    api_key = os.getenv(env_var_name)
    
    if not api_key:
        logger.error(f"Missing API key for {api_name}. Set {env_var_name} environment variable.")
        raise ValueError(f"API key for {api_name} not configured. Set {env_var_name} environment variable.")
    
    return api_key


def get_key_id(api_name: str) -> str:
    """
    Get the KEY_ID for a specific API from environment variables
    
    Args:
        api_name: Name of the API (e.g., "ratehawk")
        
    Returns:
        KEY_ID from environment variables, or default value if not configured
    """
    env_var_name = f"{api_name.upper()}_KEY_ID"
    key_id = os.getenv(env_var_name)
    
    # Se il KEY_ID non è configurato, restituisce il valore predefinito "5412"
    if not key_id:
        logger.info(f"Using default KEY_ID for {api_name} (5412). You can override by setting {env_var_name}.")
        return "5412"
    
    logger.info(f"Using KEY_ID for {api_name}: {key_id}")
    return key_id
