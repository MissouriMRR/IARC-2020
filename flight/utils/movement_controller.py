"""Holds all of the movement functions for our drone device"""
from flight import config
from flight.utils.latlon import LatLon
from mavsdk import System
import mavsdk as sdk
import logging
import math
import asyncio


class MovementController:
    """
    Params: Drone, Pylon
    Return: Boolean or None
    Calculates and uses gps coordinates of the drone to move to the location of the target pylon
    """

    async def move_to(
        self, drone: System, pylon: LatLon, offset: {float, int}, fly_at: int
    ) -> bool:
        """
        Function to calculate movement velocity:
        Parameters:
            Drone(System): Our drone object
            Pylon(LatLon): Targets for the drone found using GPS Latitude and Longitude
            Offset(bool): offset the move to position to avoid colllision
            Fly At(int): desired altitude to fly at
        Return:
            bool: True or false if the target is within range
            None: If we don't reach the target
        """

        count: int = 0

        async for gps in drone.telemetry.position():
            altitude: float = round(gps.relative_altitude_m, 2)
            # not allowed to go past 15m
            # at or above, go down (positive)
            # below tolerance, go up (negative)

            if altitude >= fly_at + (fly_at * config.ALT_PERCENT_ACCURACY):
                alt = config.ALT_CORRECTION_SPEED  # go down m/s
            elif altitude <= fly_at - (fly_at * config.ALT_PERCENT_ACCURACY):
                alt = -config.ALT_CORRECTION_SPEED  # go up m/s
            else:
                alt = -0.15  # don't move

            # Configure current position and store it
            lat: float = round(gps.latitude_deg, 8)
            lon: float = round(gps.longitude_deg, 8)
            current: float = LatLon(lat, lon)  # you are here

            # Only for first run through loop
            if count == 0:
                # How many degrees we need to turn in order to look at the pylon
                # Think of a unit circle
                deg_to_pylon: float = current.heading_initial(pylon)
                # Creating a new position we need to go to
                # Distance to the offset point from the pylon
                offset_point: float = pylon.offset(
                    deg_to_pylon + offset["DEG"], offset["KM"]
                )
                logging.debug(offset_point.to_string("d% %m% %S% %H"))  # you are here
            # distance we have to go in order to get to the offset point
            dist: float = current.distance(offset_point)
            # degrees needed to change to get to offset position
            deg: float = current.heading_initial(offset_point)

            # East, West
            x: float = dist * math.sin(math.radians(deg)) * 1000  # from km to m
            # North, South
            y: float = dist * math.cos(math.radians(deg)) * 1000  # from km to m

            if count == 0:
                reference_x: float = abs(x)
                reference_y: float = abs(y)

            try:
                dx = math.copysign(config.MAX_SPEED * math.cos(math.atan(y / x)), x)
                dy = math.copysign(config.MAX_SPEED * math.sin(math.atan(y / x)), y)
            except:
                dx: float = math.copysign(
                    config.MAX_SPEED
                    * math.cos(math.asin(y / (math.sqrt((x ** 2) + (y ** 2))))),
                    x,
                )
                dy: float = math.copysign(
                    config.MAX_SPEED
                    * math.sin(math.asin(y / (math.sqrt((x ** 2) + (y ** 2))))),
                    y,
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
                abs(x) <= 0.25  # reference_x * config.POINT_PERCENT_ACCURACY
                and abs(y) <= 0.25  # reference_y * config.POINT_PERCENT_ACCURACY
            ):
                await drone.offboard.set_velocity_ned(
                    sdk.offboard.VelocityNedYaw(0, 0, alt, deg)
                )
                return True
            count += 1

    async def turn(self, drone: System, deg: int) -> bool:
        """
        Turns the drone around the pylon it is currently at
        Parameters:
            Drone(System): Our drone object
        """
        count: int = 0
        async for tel in drone.telemetry.attitude_euler():
            current: float = (360 + round(tel.yaw_deg)) % 360
            if count == 0:
                temp = (current + deg) % 360

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

    async def check_altitude(self, drone: System) -> bool:
        """
        Checks the altitude of the drone to make sure that we are at our target
        Parameters:
            Drone(System): Our drone object
        """
        async for position in drone.telemetry.position():
            altitude: float = round(position.relative_altitude_m, 2)
            if altitude >= config.TAKEOFF_ALT:
                return True

    async def takeoff(self, drone: System):
        """Takes off vertically to a height defined by alt"""

        await drone.offboard.set_velocity_ned(
            sdk.offboard.VelocityNedYaw(0.0, 0.0, -1.0, 0.0)
            # Sets the velocity of the drone to be straight up
        )
        await self.check_altitude(drone)
        # Waits until altitude TAKEOFF_ALT is reached, before moving on to EarlyLaps

        return

    async def manual_land(self, drone: System) -> None:
        """
        Function to slowly land the drone vertically
        Parameters:
                drone(System): our drone object
        Return:
            None
        """
        # Lands the drone using manual velocity values
        logging.info("Landing the drone")
        async for position in drone.telemetry.position():
            current_altitude: float = round(position.relative_altitude_m, 3)
            if current_altitude > 1.0:
                # Descends at 0.7 m/s at altitudes > 1 m
                await drone.offboard.set_velocity_body(
                    sdk.offboard.VelocityBodyYawspeed(0.0, 0.0, 0.7, 0.0)
                )
            elif 1.0 > current_altitude > 0.3:
                # Descends at 0.35 m/s at altitudes < 1 m && > 0.3 m
                await drone.offboard.set_velocity_body(
                    sdk.offboard.VelocityBodyYawspeed(0.0, 0.0, 0.35, 0.0)
                )
            else:
                # Sets downward velocity to 0 otherwise
                await drone.offboard.set_velocity_body(
                    sdk.offboard.VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
                )
                return

    async def turn_right(self, drone: System, deg: int) -> bool:
        """
        Turns the drone around the pylon it is currently at
        Parameters:
            Drone(System): Our drone object
        """
        count: int = 0
        async for tel in drone.telemetry.attitude_euler():
            current: float = (360 + round(tel.yaw_deg)) % 360
            if count == 0:
                temp = (current + deg) % 360

            await drone.offboard.set_velocity_body(
                sdk.offboard.VelocityBodyYawspeed(5, 3, -0.1, 60)
            )
            # await asyncio.sleep(config.FAST_THINK_S)
            val = abs(current - temp)
            # TODO: Add case so that it can overshoot the point and still complete
            if val < 10:
                logging.debug("Finished Turn")
                return True
            count += 1
