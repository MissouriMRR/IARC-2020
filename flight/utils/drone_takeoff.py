import asyncio
import logging
import math
import mavsdk as sdk
from mavsdk import System

up_speed: int = -2

async def wait_alt(drone: System) -> bool:
    """Checks to see if the drone is near the target altitude"""
    async for position in drone.telemetry.position():
        altitude: float = round(position.relative_altitude_m, 2)
        if altitude >= 2:
            return True

async def getPosition(drone: System, target_lat: float, target_lon: float):
    """Gets x and y distance between 2 sets of latitude and longitude points"""

    async for gps in drone.telemetry.position():
        altitude = round(gps.relative_altitude_m, 2)

        # Find the current latitude and longitude positions
        curr_lat = round(gps.latitude_deg, 8)
        curr_lon = round(gps.longitude_deg, 8)

        x = ((target_lon - curr_lon)* 40000 * math.cos((target_lat + curr_lat) * math.pi / 360) / 360) * 1000

        y = ((target_lat - curr_lat) * 40000 / 360) * 1000

        return (x, y, altitude)

async def getVelocity(drone: System, target_lat: float, target_lon: float):
    """Returns the needed x-velocity dx, y-velocity \
       dy, altitude speed, and needed degree deg of \
       the drone to go to a given position."""
    """Returns a list of the format (dx, dy, alt, deg)"""

    # Get x and y distance from target lat and lon points, and
    # altitude
    position = await getPosition(drone, target_lat, target_lon)

    x = position[0]
    y = position[1]
    altitude = position[2]

    if altitude >= 3:
        alt = 0.2
    elif altitude <= 2:
        alt = -0.2
    else:
        alt = 0

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

    return (dx, dy, alt, deg)

async def takeoff(drone: System, target: tuple ) -> None:
    """This function expects that the drone is already armed."""
    """Function creates initial set points, starts offboard, and starts the drone \
       in the direction of the specified lat lon coordinates"""

    # Setting set points for the next 3 lines (used to basically set drone center)
    # (NSm, EWm, DUm, Ydeg)
    await drone.offboard.set_position_ned(sdk.PositionNedYaw(0.0, 0.0, 0.0, 0.0))

    # (NSm/s, EWm/s, DUm/s, Ydeg)
    await drone.offboard.set_velocity_ned(sdk.VelocityNedYaw(0.0, 0.0, 0.0, 0.0))

    # (FBm/s, RLm/s, DUm/s, Yspdeg/s)
    await drone.offboard.set_velocity_body(
        sdk.VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
    )

    try:
        # Enable offboard mode, allowing for computer to control the drone
        await drone.offboard.start()
    except sdk.OffboardError:
        await drone.action.land()
        return

    # Get target lat and lon points from the target tuple, formatted
    # (latitude, longitude)
    lat = target[0]
    lon = target[1]

    # Get the x-velocity, y-velocity, and degree to send the drone towards
    # the first pylon
    velocity = await getVelocity(drone, lat, lon)

    # X-velocity
    dx = velocity[0]
    # Y-velocity
    dy = velocity[1]
    # Degree
    deg = velocity[3]

    logging.info("Taking off towards first pylon")

    # Start the drone pointing in the direction of the first pylon
    await drone.offboard.set_velocity_ned(
        sdk.VelocityNedYaw(dy, dx, up_speed, deg)
    )

    # Loops until the desired altitude has been attained,
    # then sets the upward velocity to 0 and returns
    await wait_alt(drone)

    # If the drone has reached the desired altitude
    # Leave it moving towards the first pylon,
    # but set the upwared velocity to 0, so it stops going up
    await drone.offboard.set_velocity_ned(
        sdk.VelocityNedYaw(dy, dx, 0, deg)
    )
    return
