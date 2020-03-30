"""Runs the 8 laps to get to the mast"""
import logging
import asyncio

from .land import Land
from flight import config
from flight.utils.movement import wait_pos, wait_turn


from .land import Land


async def arange(count):
    """Needed to allows us to do a range asynchronously"""
    for i in range(count):
        yield i

class EarlyLaps:
    """Handles getting the drone around the two pylons 8 times"""

    async def run(self, drone):
        """Moves the drone to the first pylon, then begins the 8 laps"""
        # Go to pylon 1
        logging.info("Moving to pylon 1")
        await self.wait_pos(drone, config.pylon1)
        logging.info("Arrived at pylon 1")
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
