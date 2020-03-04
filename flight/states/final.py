"""Final state denotes competition over"""
from mavsdk import System

from .state import State


class Final(State):
    """This is a dead state, just exists to signify that the competition has completed"""

    async def run(self, drone: System) -> None:
        """Does nothing"""
        print("Final")
