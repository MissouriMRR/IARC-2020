"""The takeoff state"""
import asyncio
import logging
import mavsdk as sdk
from mavsdk import System

from .state import State
from .early_laps import EarlyLaps
from flight.utils.movement_controller import MovementController

from flight import config


mover: MovementController = MovementController()


class Takeoff(State):
    """The state that takes off the drone"""

    async def run(self, drone: System) -> None:
        """Arms and takes off the drone"""
        await self._check_arm_or_arm(drone)  # Arms the drone if not armed
        logging.info("Taking off")
        # Takeoff command, goes to altitude specified in params
        await drone.action.takeoff()
        # waits for altitude to be close to the specified level
        await mover.check_altitude(drone)
        logging.debug("after hold")

        # Setting set points for the next 3 lines (used to basically set drone center)
        # (NSm, EWm, DUm, Ydeg)
        await drone.offboard.set_position_ned(
            sdk.offboard.PositionNedYaw(0.0, 0.0, 0.0, 0.0)
        )

        # (NSm/s, EWm/s, DUm/s, Ydeg)
        await drone.offboard.set_velocity_ned(
            sdk.offboard.VelocityNedYaw(0.0, 0.0, 0.0, 0.0)
        )

        # (FBm/s, RLm/s, DUm/s, Yspdeg/s)
        await drone.offboard.set_velocity_body(
            sdk.offboard.VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
        )

        try:
            # Enable offboard mode, allowing for computer to control the drone
            await drone.offboard.start()
        except sdk.offboard.OffboardError:
            await drone.action.land()
            return

        return EarlyLaps()  # Return the next state, RunLaps
