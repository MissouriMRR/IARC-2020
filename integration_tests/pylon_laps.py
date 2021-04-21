#!/usr/bin/env python3
"""Integration test for performing a specific number of pylon laps"""

import os
import sys

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
gggparent_dir = os.path.dirname(ggparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir, gggparent_dir]

import logging

from flight_manager import FlightManager
from flight.state_settings import StateSettings


if __name__ == "__main__":
    try:
        state_settings: StateSettings = StateSettings()
        state_settings.enable_early_laps(True)
        state_settings.set_number_of_early_laps(8)
        state_settings.enable_to_mast(False)
        state_settings.enable_module_detection(False)

        state_settings.set_run_title("Pylon Laps Test")
        state_settings.set_run_description("Perform all 8 laps during early laps")

        flight_manager: FlightManager = FlightManager(state_settings)
        flight_manager.main()
    except:
        logging.exception("Unfixable error detected")
