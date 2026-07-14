#!/usr/bin/env python3
"""
Run script for Fake News Detection System Backend
"""

from app import app
from config.db import db
import logging
import sys


def main():
    """Main entry point"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

    logger = logging.getLogger(__name__)
    logger.info("Starting Fake News Detection System Backend...")

    # Test database connection
    try:
        db.connect()
        logger.info("Database connection successful")
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.warning("Continuing without database connection")

    # Run the application
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True
    )


if __name__ == '__main__':
    main()