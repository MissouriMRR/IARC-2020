"""Final state denotes competition over"""
from mavsdk import System

from .state import State

from vision.pipeline import Pipeline


class Final(State):
    """This is a dead state, just exists to signify that the competition has completed"""

    async def run(self, drone: System, pipeline: Pipeline = None) -> None:
        """Does nothing"""
