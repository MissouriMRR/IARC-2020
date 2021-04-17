#!/usr/bin/env python3
"""Main runnable file for the codebase"""

import logging

from flight_manager import FlightManager


if __name__ == "__main__":
    # Run multiprocessing function
    try:
        flight_manager: FlightManager = FlightManager()
        flight_manager.main()
    except:
        logging.exception("Unfixable error detected")
