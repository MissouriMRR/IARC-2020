"""After the laps, goes to the mast"""
import logging
import asyncio
import mavsdk as sdk

from flight import config

from flight.utils.movement_controller import MovementController
from .return_laps import ReturnLaps
from .state import State


class ToMast(State):
    """ Sends the drone from the first pylon to the mast """

    async def run(self, drone):
        """Sends the drone from the first pylon to the mast"""
        if self.state_settings.go_to_mast:
            mover: MovementController = MovementController()
            # Go to the mast
            logging.info("Moving to mast")
            await mover.move_to(
                drone, config.MAST_LOCATION, config.OFFSET_BACK, config.FLYING_ALT
            )
            logging.info("Arrived at mast")
            # (NSm/s, EWm/s, DUm/s, Ydeg) Stop moving
            await drone.offboard.set_velocity_ned(
                sdk.offboard.VelocityNedYaw(0.0, 0.0, -0.01, 0.0)
            )
            await asyncio.sleep(5)
            return ReturnLaps(self.state_settings)
        else:
            return ReturnLaps(self.state_settings)
