"""Runs the 8 laps to get to the mast"""
import logging
import asyncio
import mavsdk as sdk

from flight import config

from flight.utils.movement_controller import MovementController
from .state import State
from .to_mast import ToMast


async def arange(count):
    """
    Function to allow us to do a range asynchronously

    Parameters:
        count (int): max value of desired range
    Return:
        i: generator-type integer
    Logging:
        None
    """
    for i in range(count):
        yield i


class EarlyLaps(State):
    """
    Handles getting the drone around the two pylons 8 times

    Attributes:
        N/A
    Functions:
        run: Performs the movement actions for the state; movement to first pylon and first 8 laps
    """

    async def run(self, drone) -> State:
        """
        Moves the drone to the first pylon, then begins the 8 laps

        Parameters:
            drone (System): Our drone object
        Return:
            ToMast(): flight moves to next state, ToMast
        Logging:
            To info; displays lap number
            To debug; displays section of current lap - straight or turn
        """
        if config.run_states["early_laps"]:
            mover: MovementController = MovementController()
            # Go to pylon 1
            logging.info("Moving to pylon 1")
            await mover.move_to(drone, config.pylon1)
            logging.info("Arrived at pylon 1")
            async for i in arange(config.NUM_LAPS):
                logging.info("Starting lap: %d", i)
                logging.debug("Lap %d: Straight one", i)
                await mover.move_to(drone, config.pylon2)  # move to pylon 2

                logging.debug("Lap %d: Turn one", i)
                await mover.turn(drone)  # turn around pylon 2

                logging.debug("Lap %d: Straight two", i)
                await mover.move_to(drone, config.pylon1)  # move to pylon 1

                logging.debug("Lap %d: Turn two", i)
                await mover.turn(drone)  # turn around pylon 1
            return ToMast()
        else:
            return ToMast()
