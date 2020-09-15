"""State to land the drone"""
import asyncio
import logging
import mavsdk as sdk

from flight import config

from mavsdk import System

from .state import State
from .final import Final


class Land(State):
    """
    Contains the functions needed to halt and land the drone, and turns off
    offboard
    """

    async def run(self, drone: System) -> State:
        """
        Stops the drone by setting all movements to 0, then move to land
        mode
        """
        await drone.offboard.set_position_ned(sdk.offboard.PositionNedYaw(0, 0, 0, 0))
        await drone.offboard.set_velocity_ned(sdk.offboard.VelocityNedYaw(0, 0, 0, 0))
        await drone.offboard.set_velocity_body(
            sdk.offboard.VelocityBodyYawspeed(0, 0, 0, 0)
        )

        await asyncio.sleep(config.THINK_FOR_S)

        try:
            await drone.offboard.stop()
        except sdk.OffboardError as error:
            logging.exception(
                "Stopping offboard mode failed with error code: %s", str(error)
            )
            # TODO Worried about what happens here

        await asyncio.sleep(config.THINK_FOR_S)

        logging.info("Landing the drone")
        await drone.action.land()
        return Final()
