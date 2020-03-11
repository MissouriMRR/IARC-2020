"""Runs the 8 laps to get to the mast"""
import logging
import asyncio
import math
import mavsdk as sdk

from flight import config
from flight.utils.latlon import LatLon


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
        await self.wait_pos(drone, config.pylon1)
        async for i in arange(2):
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
        count = 0
        async for gps in drone.telemetry.position():
            altitude = round(gps.relative_altitude_m, 2)

            if altitude >= config.ALT_RANGE_MAX:
                alt = config.ALT_CORRECTION_SPEED  # go down m/s
            elif altitude <= config.ALT_RANGE_MIN:
                alt = -config.ALT_CORRECTION_SPEED  # go up m/s
            else:
                alt = 0  # don't move

            lat = round(gps.latitude_deg, 8)
            lon = round(gps.longitude_deg, 8)
            point1 = LatLon(lat, lon)  # you are here

            #offset pylon
            dist = point1.distance(pylon)
            deg = point1.heading_initial(pylon)

            point2 = pylon.offset(deg+config.DEG_OFFSET, config.OFFSET)
            dist = point1.distance(point2)
            deg = point1.heading_initial(point2)

            x=dist*math.sin(math.radians(deg))*1000 # from km to m
            y=dist*math.cos(math.radians(deg))*1000 # from km to m
            if count == 0:
                reference_x: float = abs(x)
                reference_y: float = abs(y)
            try:  # deturman what velocity should go at
                dx = math.copysign(config.MAX_SPEED * math.cos(math.atan(y / x)), x)
                dy = math.copysign(config.MAX_SPEED * math.sin(math.atan(y / x)), y)

            except ZeroDivisionError:
                dx = math.copysign(
                    config.MAX_SPEED * math.cos(math.asin(y / (math.sqrt((x ** 2) + (y ** 2))))), x
                )
                dy = math.copysign(
                    config.MAX_SPEED * math.sin(math.asin(y / (math.sqrt((x ** 2) + (y ** 2))))), y
                )

            await drone.offboard.set_velocity_ned(sdk.VelocityNedYaw(dy, dx, alt, deg))

            if abs(x) <= reference_x*config.POINT_PERCENT_ACCURACY and abs(y) <= reference_y*config.POINT_PERCENT_ACCURACY:
                return True
            count+=1

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
            asyncio.sleep(1)
            val = abs(current - temp)
            # Need to add case so that it can overshoot
            if val < 10:
                logging.info("Finished Turn")
                return True
            count += 1
