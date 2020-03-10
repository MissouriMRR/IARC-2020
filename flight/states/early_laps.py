"""Runs the 8 laps to get to the mast"""
import logging
import asyncio
import math
import mavsdk as sdk

from .land import Land

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
        async for gps in drone.telemetry.position():
            altitude = round(gps.relative_altitude_m, 2)
            if altitude >= 3:
                alt = 0.2
            elif altitude <= 2:
                alt = -0.2
            else:
                alt = 0
            lat = round(gps.latitude_deg, 8)
            lon = round(gps.longitude_deg, 8)
            x = (
                (goal_lon - lon)
                * 40000
                * math.cos((goal_lat + lat) * math.pi / 360)
                / 360
            ) * 1000
            y = ((goal_lat - lat) * 40000 / 360) * 1000

            try:  # calcualte what degree to point at
                deg = round((((math.atan(x / y) / math.pi) * 180)))

                if y < 0:
                    z = 180
                    z = math.copysign(z, deg)
                    deg = z + deg
            except ZeroDivisionError:
                deg = round(
                    (
                        (
                            (math.asin(x / (math.sqrt((x ** 2) + (y ** 2)))) / math.pi)
                            * 180
                        )
                    )
                )

                if y < 0:
                    z = 180
                    deg = -deg
                    z = math.copysign(z, deg)
                    deg = z + deg

            try:  # deturman what velocity should go at
                dx = math.copysign(35 * math.cos(math.atan(y / x)), x)
                dy = math.copysign(35 * math.sin(math.atan(y / x)), y)

            except ZeroDivisionError:
                dx = math.copysign(
                    35 * math.cos(math.asin(y / (math.sqrt((x ** 2) + (y ** 2))))), x
                )
                dy = math.copysign(
                    35 * math.sin(math.asin(y / (math.sqrt((x ** 2) + (y ** 2))))), y
                )

            await drone.offboard.set_velocity_ned(sdk.VelocityNedYaw(dy, dx, alt, deg))

            if abs(x) <= 10 and abs(y) <= 10:
                return True

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
