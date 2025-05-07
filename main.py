"""
Main entry point for the application.
This file is required for the Flask server to run.
"""

import logging
from app import app  # noqa: F401

# Configure logging
logging.basicConfig(level=logging.DEBUG, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)
logger.info("Application started")

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000, debug=True)
