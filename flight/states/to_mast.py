"""After the laps, goes to the mast"""
import logging
import asyncio
import mavsdk as sdk

from mavsdk import System
from flight import config

from flight.utils.movement_controller import MovementController
from .land import Land
from .state import State
from vision.pipeline import Pipeline


class ToMast(State):
    """ Sends the drone from the first pylon to the mast """

    async def run(self, drone: System, pipeline: Pipeline = None):
        """Sends the drone from the first pylon to the mast"""
        if config.USE_VISION:
            pipeline.flight_communication.put_nowait("to_mast")
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
