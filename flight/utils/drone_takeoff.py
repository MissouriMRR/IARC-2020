import asyncio
import logging
import math
import mavsdk as sdk
from mavsdk import System
from flight.utils.movement import get_velocity, wait_alt

async def takeoff(drone: System, pylon ) -> None:
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

    # Get the x-velocity, y-velocity, and degree to send the drone towards
    # the first pylon
    velocity = await get_velocity(drone, pylon)

    # X-velocity
    dx = velocity[0]
    # Y-velocity
    dy = velocity[1]
    # Up speed
    alt = velocity[2]
    # Degree
    deg = velocity[3]

    logging.info("Taking off towards first pylon")

    # Start the drone pointing in the direction of the first pylon
    await drone.offboard.set_velocity_ned(
        sdk.VelocityNedYaw(dy, dx, -.5, deg)
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
