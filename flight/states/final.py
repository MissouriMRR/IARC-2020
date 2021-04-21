"""Final state denotes competition over"""
from mavsdk import System

from .state import State


class Final(State):
    """
    This is a dead state, just exists to signify that the competition has completed

    Attributes:
        N/A
    Functions:
        run: Perform the state's actions; in this case nothing occurs
    """

    async def run(self, drone: System) -> None:
        """
        Does nothing, end current flight run

        Parameters:
            drone (System): Our drone object
        Return:
            None
        Logging:
            None
        """
