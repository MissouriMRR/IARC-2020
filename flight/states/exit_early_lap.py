"""Runs the Final lab to move to mast"""
import logging
import asyncio
import mavsdk as sdk

from flight import config

from flight.utils.movement_controller import MovementController
from .state import State
from .to_mast import ToMast


class ExitEarlyLap(State):
    """Handles getting the drone around the two pylons for the final times"""

    async def run(self, drone):
        """Runs the final lap"""
        if config.run_states["early_laps"]:
            mover: MovementController = MovementController()

            logging.info("Starting final lap")
            logging.debug("Final Lap: Straight one")
            await mover.move_to(
                drone, config.pylon2, config.OFFSET_RIGHT, config.FLYING_ALT
            )  # move to pylon 2

            logging.debug("Final Lap: Turn one")
            await mover.turn(drone, 180)  # turn around pylon 2

            logging.debug("Final Lap: Straight two")
            await mover.move_to(
                drone, config.pylon1, config.OFFSET_RIGHT, config.FLYING_ALT
            )  # move to pylon 1

            logging.debug("Final Lap: Turn two")
            await mover.turn(drone, -90)  # turn around pylon 1
            return ToMast()
        else:
            return ToMast()
