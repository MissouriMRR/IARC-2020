"""Base State class which all other states inherit"""
from mavsdk import System


class State:
    """
    Base State class

    Attributes:
        drone (System): The drone object; used for flight.
    """

    async def run(self, drone: System):
        """
        Does all of the operations for the state

        Parameters
        ----------
        drone : System
            The drone system; used for flight operations.

        Returns
        -------
        State or None
            Either the next State in the machine or None if the machine stops

        Raises
        ------
        Exception
            If this function hasn't been overloaded.
        """
        raise Exception("Run not implemented for state")

    async def _check_arm_or_arm(self, drone: System):
        """
        Verifies that the drone is armed, if not armed, arms the drone

        Parameters
        ----------
        drone : System
            The drone system; used for flight operations.
        """
        async for is_armed in drone.telemetry.armed():
            if not is_armed:
                print("Not armed -- Arming")
                await drone.action.arm()
            else:
                print("Armed -- Continuing")
                break
