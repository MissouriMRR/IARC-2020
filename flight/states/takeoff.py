"""The takeoff state"""
import asyncio
from mavsdk import System

from .state import State
from .early_laps import EarlyLaps
from ..utils.drone_takeoff import takeoff
from flight.config import pylon1


class Takeoff(State):
    """The state that takes off the drone"""

    async def run(self, drone: System) -> None:
        """Arms and takes off the drone"""
        await self._check_arm_or_arm(drone)  # Arms the drone if not armed

        # Start drone in direction of the first pylon
        await takeoff( drone, pylon1 )

        # Start laps after desired altitude is reached
        return EarlyLaps()  # Return the next state, RunLaps
