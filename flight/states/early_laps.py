"""Runs the 8 laps to get to the mast"""
import logging
import asyncio
import math
import mavsdk as sdk

from .land import Land
from ..utils.drone_takeoff import getPosition, getVelocity

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
        await self.wait_pos(drone, lat1, lon1)
        async for i in arange(8):
            logging.info("Starting lap: %d", i)
            logging.debug("Lap %d: Straight one", i)
            await self.wait_pos(drone, lat2, lon2)  # move to pylon 2

            logging.debug("Lap %d: Turn one", i)
            await self.wait_turn(drone)  # turn around pylon 2

            logging.debug("Lap %d: Straight two", i)
            await self.wait_pos(drone, lat1, lon1)  # move to pylon 1

            logging.debug("Lap %d: Turn two", i)
            await self.wait_turn(drone)  # turn around pylon 1
        return Land()

    async def wait_pos(self, drone, goal_lat, goal_lon):
        """Goes to a position"""

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

                if abs(x) <= 10 and abs(y) <= 10:
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
                sdk.VelocityBodyYawspeed(60, -55, 0.25, -90)
            )
            if current == temp:
                return True
            count += 1
