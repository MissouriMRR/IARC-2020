"""The first state of competition, starts the takeoff state"""
from mavsdk import System

from .state import State
from .takeoff import Takeoff


class Start(State):
    """The starting state of the flight state machine"""

    async def run(self, drone: System) -> State:
        """Begins the state machine and returns the takeoff state"""
        return Takeoff()
