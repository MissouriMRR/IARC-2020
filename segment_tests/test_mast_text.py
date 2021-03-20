#!/usr/bin/env python3
"""Segment test for running mast text detection directly from takeoff"""

import logging
from flight_manager import FlightManager
from flight.state_settings import StateSettings


if __name__ == "__main__":
    try:
        state_settings: StateSettings = StateSettings()
        state_settings.set_early_laps(False)
        state_settings.set_number_of_early_laps(0)
        state_settings.set_to_mast(False)
        state_settings.set_detect_module(True)
        state_settings.enable_simple_takeoff(True)
        state_settings.set_vision_test("text")

        flight_manager: FlightManager = FlightManager(state_settings)
        flight_manager.main()
    except:
        logging.exception("Unfixable error detected")
