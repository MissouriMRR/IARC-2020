"""The takeoff state"""
import asyncio
import logging
import math
import mavsdk as sdk
from mavsdk import System

from .state import State
from .early_laps import EarlyLaps
from .early_laps import lat1 as target_lat
from .early_laps import lon1 as target_lon
from ..utils.drone_takeoff import takeoff

from flight import config


class Takeoff(State):
    """The state that takes off the drone"""

    async def run(self, drone: System) -> None:
        """Arms and takes off the drone"""
        await self._check_arm_or_arm(drone)  # Arms the drone if not armed

        # Setting set points for the next 3 lines (used to basically set drone center)
        # (NSm, EWm, DUm, Ydeg)
        await drone.offboard.set_position_ned(sdk.PositionNedYaw(0.0, 0.0, 0.0, 0.0))

        # (NSm/s, EWm/s, DUm/s, Ydeg)
        await drone.offboard.set_velocity_ned(sdk.VelocityNedYaw(0.0, 0.0, 0.0, 0.0))

        # (FBm/s, RLm/s, DUm/s, Yspdeg/s)
        await drone.offboard.set_velocity_body(
            sdk.VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
        )

        try:
            # Enable offboard mode, allowing for computer to control the drone
            await drone.offboard.start()
        except sdk.OffboardError:
            await drone.action.land()
            return

        # Start drone in direction of the first pylon
        await takeoff( drone, (target_lat, target_lon) )

        # Start laps after desired altitude is reached
        return EarlyLaps()  # Return the next state, RunLaps
