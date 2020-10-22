from flight import config
from flight.utils.latlon import LatLon
from mavsdk import System
import mavsdk as sdk
import logging
import asyncio
import math

class D_Move:
    """
    Params: Drone, Pylon
    Calculates and uses gps coordinates of the drone to move to the location of the target pylon 
    """
    async def moveTo(self, drone: System, pylon: LatLon):
        count = 0

        async for gps in drone.telemetry.position():
            altitude = round(gps.relative_altitude_m, 2)
            #not allowed to go past 15m
            #at or above, go down (positive)
            #below tolerance, go up (negative)

            if altitude >= config.ALT_RANGE_MAX:
                alt = config.ALT_CORRECTION_SPEED  # go down m/s
            elif altitude <= config.ALT_RANGE_MIN:
                alt = -config.ALT_CORRECTION_SPEED  # go up m/s
            else:
                alt = -0.15  # don't move

            #Configure current position and store it
            lat = round(gps.latitude_deg, 8)
            lon = round(gps.longitude_deg, 8)
            current = LatLon(lat, lon)  # you are here

            #Only for first run through loop
            if count == 0:
                # How many degrees we need to turn in order to look at the pylon
                # Think of a unit circle
                deg_to_pylon = current.heading_initial(pylon)
                # Creating a new position we need to go to
                # Distance to the offset point from the pylon
                offset_point = pylon.offset(
                    deg_to_pylon + config.DEG_OFFSET, config.OFFSET
                )
                logging.debug(offset_point.to_string("d% %m% %S% %H"))  # you are here
            # distance we have to go in order to get to the offset point
            dist = current.distance(offset_point)
            # degrees needed to change to get to offset position
            deg = current.heading_initial(offset_point)

            #East, West
            x = dist * math.sin(math.radians(deg)) * 1000  # from km to m
            # North, South
            y = dist * math.cos(math.radians(deg)) * 1000  # from km to m

            if count == 0:
                reference_x: float = abs(x)
                reference_y: float = abs(y)

                dx = math.copysign(
                    config.MAX_SPEED
                    * math.cos(math.asin(y / (math.sqrt((x ** 2) + (y ** 2))))),
                    x
                )
                dy = math.copysign(
                    config.MAX_SPEED
                    * math.sin(math.asin(y / (math.sqrt((x ** 2) + (y ** 2))))),
                    y
                )
            # continuously update information on the drone's location
            # and update the velocity of the drone
            await drone.offboard.set_velocity_ned(
                sdk.offboard.VelocityNedYaw(dy, dx, alt, deg)
            )
            # if the x and y values are close enough (2m) to the original position * precision
            # if inside the circle, move on to the next
            # if outside of the circle, keep running to you get inside
            if (
                abs(x) <= reference_x * config.POINT_PERCENT_ACCURACY
                and abs(y) <= reference_y * config.POINT_PERCENT_ACCURACY
            ):
                return True
            count += 1
            
    """
    Params: Drone
    Turns the drone 180 degrees around the pylon it is currently at
    """
    async def turnTo(self, drone: System):
        count = 0
        async for tel in drone.telemetry.attitude_euler():
            current = (360 + round(tel.yaw_deg)) % 360
            if count == 0:
                temp = (current + 180) % 360

            await drone.offboard.set_velocity_body(
                sdk.offboard.VelocityBodyYawspeed(5, -3, -0.1, -60)
            )
            # await asyncio.sleep(config.FAST_THINK_S)
            val = abs(current - temp)
            # TODO: Add case so that it can overshoot the point and still complete
            if val < 10:
                logging.debug("Finished Turn")
                return True
            count += 1

    """
    Params: Drone
    Checks the altitude of the drone to make sure that we are at our target
    """
    async def checkAlt(self, drone: System):
        async for position in drone.telemetry.position():
            altitude: float = round(position.relative_altitude_m, 2)
            if altitude >= config.ALT_RANGE_MIN:
                return True