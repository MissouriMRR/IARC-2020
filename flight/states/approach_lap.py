"""Approach pylon for 8 laps to get to the mast"""
import logging
import asyncio
import math
import mavsdk as sdk
from mavsdk import System

from flight import config
from flight.utils.latlon import LatLon
#from latlon import LatLon


from .run_laps import RunLaps

class ApproachLap:
    """Handles getting the drone first pylon"""

    async def run(self, drone: System):
        """Moves the drone to the first pylon"""
        # Go to pylon 1
        logging.info("Moving to pylon 1")
        await self.wait_pos(drone, config.pylon1)
        logging.info("Arrived at pylon 1")

        return RunLaps()

    async def wait_pos(self, drone: System, pylon: LatLon):
        """Goes to a position"""
        count = 0
        async for gps in drone.telemetry.position():
            altitude = round(gps.relative_altitude_m, 2)

            if altitude >= config.ALT_RANGE_MAX:
                alt = config.ALT_CORRECTION_SPEED  # go down m/s
            elif altitude <= config.ALT_RANGE_MIN:
                alt = -config.ALT_CORRECTION_SPEED  # go up m/s
            else:
                alt = -0.15  # don't move

            lat = round(gps.latitude_deg, 8)
            lon = round(gps.longitude_deg, 8)
            current = LatLon(lat, lon)  # you are here

            if count==0:
                #offset pylon
                deg_to_pylon = current.heading_initial(pylon)
                offset_point = pylon.offset(deg_to_pylon+config.DEG_OFFSET, config.OFFSET)
                logging.debug(offset_point.to_string('d% %m% %S% %H'))# you are here

            dist = current.distance(offset_point)
            deg = current.heading_initial(offset_point)

            x=dist*math.sin(math.radians(deg))*1000 # from km to m
            y=dist*math.cos(math.radians(deg))*1000 # from km to m
            if count == 0:
                reference_x: float = abs(x)
                reference_y: float = abs(y)
            try:  # determine what velocity should go at
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
