import asyncio
import logging
import math
import mavsdk as sdk
from mavsdk import System

up_speed: int = -2

async def wait_alt(drone: System):
    """Checks to see if the drone is near the target altitude"""
    async for position in drone.telemetry.position():
        altitude: float = round(position.relative_altitude_m, 2)
        if altitude >= 2:
            return True

async def takeoff(drone: System, target: tuple ) -> None:

    target_lat = target[0]
    target_lon = target[1]

    logging.info("Taking off towards first pylon")

    async for gps in drone.telemetry.position():

        # Find the current latitude and longitude positions
        curr_lat = round(gps.latitude_deg, 8)
        curr_lon = round(gps.longitude_deg, 8)

        x = ((target_lon - curr_lon)* 40000 * math.cos((target_lat + curr_lat) * math.pi / 360) / 360) * 1000

        y = ((target_lat - curr_lat) * 40000 / 360) * 1000

        # Calculate the degree to point the drone at
        try:
            deg = round((((math.atan(x / y) / math.pi) * 180)))

            if y < 0:
                z = 180
                z = math.copysign(z, deg)
                deg = z + deg
        except ZeroDivisionError:
            deg = round((((math.asin(x / (math.sqrt((x ** 2) + (y ** 2)))) / math.pi)* 180)))

            if y < 0:
                z = 180
                z = math.copysign(z, deg)
                deg = z + deg

        # Calculate the needed velocity needed to reach the target lat lon points
        try:
            dx = math.copysign(35 * math.cos(math.atan(y / x)), x)
            dy = math.copysign(35 * math.sin(math.atan(y / x)), y)

        except ZeroDivisionError:
            dx = math.copysign(35 * math.cos(math.asin(y / (math.sqrt((x ** 2) + (y ** 2))))), x)
            dy = math.copysign(35 * math.sin(math.asin(y / (math.sqrt((x ** 2) + (y ** 2))))), y)

        # Start the drone pointing in the direction of the first pylon
        await drone.offboard.set_velocity_ned(
            sdk.VelocityNedYaw(dy, dx, up_speed, deg)
        )

        # Loops until the desired altitude has been attained,
        # then sets the upward velocity to 0 and returns
        if await wait_alt(drone):
            # If the drone has reached the desired altitude
            # Leave it moving towards the first pylon,
            # but set the upwared velocity to 0, so it stops going up
            await drone.offboard.set_velocity_ned(
                sdk.VelocityNedYaw(dy, dx, 0, deg)
            )
            return
