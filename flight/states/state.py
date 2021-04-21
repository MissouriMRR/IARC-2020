"""Base State class which all other states inherit"""
import logging
from mavsdk import System


class State:
    """
    Base State class

    Attributes:
        N/A
    Functions:
        __init__: Displays to logging information the name of the current state
        run: Performs the actions for a specific state
        _check_arm_or_disarm: Checks to see if drone is armed; if not, arms it
        name: Returns the name of the current state
    """

    def __init__(self):
        logging.info('State "%s" has begun', self.name)

    async def run(self, drone: System):
        """
        Does all of the operations for the state

        Parameters:
            drone (System): The drone system; used for flight operations.
        Return:
            State or None: Either the next State in the machine or None if the machine stops
        Raises:
            Exception: If this function hasn't been overloaded.
        """
        raise Exception("Run not implemented for state")

    async def _check_arm_or_arm(self, drone: System) -> None:
        """
        Verifies that the drone is armed, if not armed, arms the drone

        Parameters:
            drone (System): The drone system; used for flight operations.
        Return:
            None
        Logging:
            To debug; drone fails to arm, attempt to re-arm
        """
        async for is_armed in drone.telemetry.armed():
            if not is_armed:
                logging.debug("Not armed. Attempting to arm")
                await drone.action.arm()
            else:
                logging.warning("Drone armed")
                break

    @property
    def name(self) -> str:
        """
        Returns the name of the class

        Parameters:
            N/A
        Return:
            __name__: Name of current state
        Logging:
            None
        """
        return type(self).__name__
