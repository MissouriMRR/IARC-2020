import logging
import asyncio
import math

import mavsdk as sdk
from mavsdk import System
from flight.utils.latlon.lat_lon import LatLon
from flight import config


async def wait_alt(drone: System) -> bool:
    """Checks to see if the drone is near the target altitude"""
    async for position in drone.telemetry.position():
        altitude: float = round(position.relative_altitude_m, 2)
        if altitude >= 2:
            return True

async def get_distance(drone: System, pylon):
    """Gets x and y distance between 2 sets of latitude and longitude points"""

    async for gps in drone.telemetry.position():
        altitude = round(gps.relative_altitude_m, 2)

        # Find the current latitude and longitude positions
        curr_lat = round(gps.latitude_deg, 8)
        curr_lon = round(gps.longitude_deg, 8)

        current = LatLon(curr_lat, curr_lon)

        deg_to_pylon = current.heading_initial(pylon)
        offset_point = pylon.offset(deg_to_pylon + config.DEG_OFFSET, config.OFFSET)

        dist = current.distance(offset_point)
        deg = current.heading_initial(offset_point)

        x = dist*math.sin(math.radians(deg))*1000
        y = dist*math.cos(math.radians(deg))*1000

        return (x, y, altitude, deg)

async def get_velocity(drone: System, pylon):
    """Returns the needed x-velocity dx, y-velocity \
       dy, altitude speed, and needed degree deg of \
       the drone to go to a given position."""
    """Returns a list of the format (dx, dy, alt, deg)"""

    # Get x and y distance from target lat and lon points, and
    # altitude
    distance = await get_distance(drone, pylon)

    x = distance[0]
    y = distance[1]
    altitude = distance[2]
    deg = distance[3]

    if altitude >= 3:
        alt = config.ALT_CORRECTION_SPEED
    elif altitude <= 2:
        alt = -config.ALT_CORRECTION_SPEED
    else:
        alt = 0

    # Calculate the needed velocity needed to reach the target lat lon points
    try:
        dx = math.copysign( config.MAX_SPEED * math.cos( math.atan( y / x) ), x)
        dy = math.copysign( config.MAX_SPEED * math.sin( math.atan( y / x) ), y)

    except ZeroDivisionError:
        dx = math.copysign( config.MAX_SPEED * math.cos( math.asin( y / ( math.sqrt( x**2 + y**2 )))), x )
        dy = math.copysign( config.MAX_SPEED * math.sin( math.asin( y / ( math.sqrt( x**2 + y**2 )))), y )

    return (dx, dy, alt, deg)

async def wait_pos(drone, pylon):
    """Goes to a position"""

    # Get the x-velocity, y-velocity, and degree to send the drone towards
    # the first pylon
    velocity = await get_velocity(drone, pylon)

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

    asyncio.ensure_future(check_at_pos)

async def check_at_pos(drone: System, pylon)

    distance = await get_distance(drone, pylon)
    reference_x = abs(distance[0])
    reference_y = abs(distance[1])

    # Loop until the drone is close to the given position
    while True:
        try:
            distance = await get_distance(drone, pylon)
            x = distance[0]
            y = distance[1]

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
            return True

async def wait_turn(drone):
    """Completes a full turn"""
    count = 0
    async for tel in drone.telemetry.attitude_euler():
        current = (360 + round(tel.yaw_deg)) % 360
        if count == 0:
            temp = (current + 180) % 360

        await drone.offboard.set_velocity_body(
            sdk.VelocityBodyYawspeed(5, -3, -0.1, -60)
        )

        await asyncio.sleep(1)
        val = abs(current - temp)
        if val < 10:
            logging.info("Finished Turn")
            return True
        count += 1
