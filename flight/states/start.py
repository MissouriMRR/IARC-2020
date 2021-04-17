"""The first state of competition, starts the takeoff state"""
from mavsdk import System

from .state import State
from .takeoff import Takeoff
from .simple_takeoff import SimpleTakeoff


class Start(State):
    """The starting state of the flight state machine"""

    async def run(self, drone: System) -> State:
        """Begins the state machine and returns the takeoff state"""
        if self.state_settings.simple_takeoff:
            return SimpleTakeoff(self.state_settings)

        return Takeoff(self.state_settings)
