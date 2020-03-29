"""Runs the 8 laps to get to the mast"""
import logging
import asyncio
import math
import mavsdk as sdk

from .land import Land
from flight.utils.latlon.lat_lon import LatLon
from flight import config
from ..utils.drone_takeoff import getPosition, getVelocity


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
            await self.wait_pos(drone, config.pylon2)  # move to pylon 2

            logging.debug("Lap %d: Turn one", i)
            await self.wait_turn(drone)  # turn around pylon 2

            logging.debug("Lap %d: Straight two", i)
            await self.wait_pos(drone, config.pylon1)  # move to pylon 1

            logging.debug("Lap %d: Turn two", i)
            await self.wait_turn(drone)  # turn around pylon 1
        return Land()

    async def wait_pos(self, drone, pylon):
        """Goes to a position"""

        position = await getPosition(drone, goal_lat, goal_lon)
        reference_x = abs(position[0])
        reference_y = abs(position[1])

        # Get the x-velocity, y-velocity, and degree to send the drone towards
        # the first pylon
        velocity = await getVelocity(drone, goal_lat, goal_lon)

        # X-velocity
        dx = velocity[0]
        # Y-velocity
        dy = velocity[1]
        # Altitude
        alt = velocity[2]
        # Degree
        deg = velocity[3]

        # Start the drone towards the given position
        await drone.offboard.set_velocity_ned(sdk.VelocityNedYaw(dy, dx, alt, deg))

        # Loop until the drone is close to the given position
        while True:
            try:
                position = await getPosition(drone, goal_lat, goal_lon)
                x = position[0]
                y = position[1]

                if abs(x) <= reference_x*config.POINT_PERCENT_ACCURACY and abs(y) <= reference_y*config.POINT_PERCENT_ACCURACY:
                    return True
            # NOTE: Found a weird bug where if Ctrl+C was pressed while enroute to the
            # first pylon, the drone would continue on forever
            # Added this as a fail safe.  If Ctrl+C is pressed and the exception
            # is not caught in run.py for whatever reason, set all velocities to 0
            # and land the drone at whatver the current position is
            # NOTE: should update to land at specific point once manual land is implemented
            except KeyboardInterrupt:
                drone.offboard.set_velocity_ned(sdk.VelocityNedYaw(0.0,0.0,0.0,0.0))
                drone.action.land()

    async def wait_turn(self, drone):
        """Completes a full turn"""
        count = 0
        async for tel in drone.telemetry.attitude_euler():
            current = (360 + round(tel.yaw_deg)) % 360
            if count == 0:
                temp = (current + 180) % 360

            await drone.offboard.set_velocity_body(
                sdk.VelocityBodyYawspeed(5, -3, -0.1, -60)
            )
            await asyncio.sleep(config.FAST_THINK_S)
            val = abs(current - temp)
            # TODO: Add case so that it can overshoot the point and still complete
            if val < 10:
                logging.debug("Finished Turn")
                return True
            count += 1
