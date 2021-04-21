"""After the laps, goes to the mast"""
import logging
import asyncio
import mavsdk as sdk

from flight import config

from flight.utils.movement_controller import MovementController
from .land import Land
from .state import State


class ToMast(State):
    """
    Sends the drone from the first pylon to the mast

    Attributes:
        N/A
    Functions:
        run: Performs movement actions for the drone; maneuvers the drone to the mast
    """

    async def run(self, drone) -> State:
        """
        Sends the drone from the first pylon to the mast

        Parameters:
            drone (System): Our drone object
        Return:
            Land(): flight moves to next state, Land
        Logging:
            To info; confirms movement to mast
                     confirms arrival at mast
        """
        if config.run_states["to_mast"]:
            mover: MovementController = MovementController()
            # Go to the mast
            logging.info("Moving to mast")
            await mover.move_to(drone, config.MAST_LOCATION)
            logging.info("Arrived at mast")
            # (NSm/s, EWm/s, DUm/s, Ydeg) Stop moving
            await drone.offboard.set_velocity_ned(
                sdk.offboard.VelocityNedYaw(0.0, 0.0, 0.0, 0.0)
            )
            await asyncio.sleep(20)
            return Land()
        else:
            return Land()
