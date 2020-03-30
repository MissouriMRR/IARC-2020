"""Runs the 8 laps to get to the mast"""
import logging
import asyncio

from .land import Land
from flight import config
from flight.utils.movement import wait_pos, wait_turn

# Position for pylon 1
lat1: int = 37.9489551
lon1: int = -91.7844405

# Position for pylon 2
lat2: int = 37.9486433
lon2: int = -91.7839372


async def arange(count):
    """Needed to allows us to do a range asynchronously"""
    for i in range(count):
        yield i

class EarlyLaps:
    """Handles getting the drone around the two pylons 8 times"""

    async def run(self, drone):
        """Moves the drone to the first pylon, then begins the 8 laps"""
        # Go to pylon 1
        await wait_pos( drone, config.pylon1 )

        async for i in arange(config.NUM_LAPS):
            logging.info("Starting lap: %d", i)
            logging.debug("Lap %d: Straight one", i)
            await wait_pos(drone, config.pylon2)  # move to pylon 2

            logging.debug("Lap %d: Turn one", i)
            await wait_turn(drone)  # turn around pylon 2

            logging.debug("Lap %d: Straight two", i)
            await wait_pos(drone, config.pylon1)  # move to pylon 1

            logging.debug("Lap %d: Turn two", i)
            await wait_turn(drone)  # turn around pylon 1
        return Land()
