""""""
import logging
import asyncio
import mavsdk as sdk

from flight import config

from flight.utils.movement_controller import MovementController
from .state import State
from .exit_return_lap import ExitReturnLap


async def arange(count):
    """Needed to allows us to do a range asynchronously"""
    for i in range(count):
        yield i


class ReturnLaps(State):
    """"""

    async def run(self, drone):
        """"""
        if self.state_settings.do_return_laps:
            mover: MovementController = MovementController()
            # Go to pylon 1
            logging.info("Moving to pylon 1")
            await mover.move_to(
                drone, config.pylon1, config.OFFSET_LEFT, config.FLYING_ALT
            )

            logging.info("Arrived at pylon 1")
            async for i in arange(config.NUM_LAPS - 1):

                logging.info("Starting lap: %d", i)
                logging.debug("Lap %d: Straight one", i)
                await mover.move_to(
                    drone, config.pylon2, config.OFFSET_LEFT, config.FLYING_ALT
                )  # move to pylon 2

                logging.debug("Lap %d: Turn one", i)
                await mover.turn_right(drone, 180)  # turn around pylon 2

                logging.debug("Lap %d: Straight two", i)
                await mover.move_to(
                    drone, config.pylon1, config.OFFSET_LEFT, config.FLYING_ALT
                )  # move to pylon 1

                logging.debug("Lap %d: Turn two", i)
                await mover.turn_right(drone, 180)  # turn around pylon 1
            return ExitReturnLap(self.state_settings)
        else:
            return ExitReturnLap(self.state_settings)
