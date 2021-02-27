#!/usr/bin/env python3
"""Segment test for module detection at the mast"""

import logging

from flight_manager import FlightManager
from flight.state_settings import StateSettings


if __name__ == "__main__":
    try:
        state_settings: StateSettings = StateSettings()
        state_settings.set_early_laps(True)
        state_settings.set_number_of_early_laps(1)
        state_settings.set_to_mast(True)
        state_settings.set_detect_module(True)

        flight_manager: FlightManager = FlightManager(state_settings)
        flight_manager.main()
    except:
        logging.exception("Unfixable error detected")
