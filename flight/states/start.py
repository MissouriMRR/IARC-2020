"""The first state of competition, starts the takeoff state"""
from mavsdk import System
from flight import config

from .state import State
from .takeoff import Takeoff
from vision.pipeline import Pipeline


class Start(State):
    """The starting state of the flight state machine"""

    async def run(self, drone: System, pipeline: Pipeline = None) -> State:
        """Begins the state machine and returns the takeoff state"""
        if config.USE_VISION:
            pipeline.flight_communication.put_nowait("start")
        return Takeoff()
