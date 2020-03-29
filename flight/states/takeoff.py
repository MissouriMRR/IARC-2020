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
