"""The takeoff state"""
import asyncio
import logging
import math
import mavsdk as sdk
from mavsdk import System

from .state import State
from .early_laps import EarlyLaps
from .early_laps import lat1 as target_lat
from .early_laps import lon1 as target_lon

from flight import config


class Takeoff(State):
    """The state that takes off the drone"""

    async def run(self, drone: System) -> None:
        """Arms and takes off the drone"""
        await self._check_arm_or_arm(drone)  # Arms the drone if not armed
        logging.info("Taking off")

        # await drone.action.takeoff()
        # waits for altitude to be close to the specified level
        # await self.wait_alt(drone)

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

        # Probably need to put takeoff() here (before EarlyLaps())
        # await self.test_takeoff(drone)
        await self.takeoff(drone)
        return EarlyLaps()  # Return the next state, RunLaps

    async def wait_alt(self, drone: System):
        """Checks to see if the drone is near the target altitude"""
        async for position in drone.telemetry.position():
            altitude: float = round(position.relative_altitude_m, 2)
            if altitude >= config.ALT_RANGE_MIN:
                return True


    async def takeoff(self, drone: System) -> None:
        logging.info("Taking off")

        # Need to calculate current position relative to lat and lon

        up_speed: float = -.5

        async for gps in drone.telemetry.position():

            # Find the current latitude and longitude positions
            curr_lat = round(gps.latitude_deg, 8)
            curr_lon = round(gps.longitude_deg, 8)

            break

        x = ( (target_lon - curr_lon) * 40000 * math.cos( (target_lat + curr_lat) * math.pi / 360) / 360 ) * 1000

        y = ( (target_lat - curr_lat) * 40000 / 360) * 1000

        # Calculate the degree to point the drone at
        try:
            deg = round(((( math.atan(x / y) / math.pi) *180)))

            if y < 0:
                z = 180
                z = math.copysign(z, deg)
                deg = z + deg
        except ZeroDivisionError:
            deg = round(((( math.asin( x / ( math.sqrt(( x**2 ) + ( y**2 )))) / math.pi) * 180 )))

            if y < 0:
                z = 180
                z = math.copysign(z, deg)
                deg = z + deg

        # Calculate the needed velocity for x and y
        try:
            dx = math.copysign(35 * math.cos(math.atan(y / x)), x)
            dy = math.copysign(35 * math.sin(math.atan(y / x)), y)

        except ZeroDivisionError:
            dx = math.copysign(
                    35 * math.cos(math.asin(y / (math.sqrt((x**2) + (y**2))))), x
            )
            dy = math.copysign(
                    35 * math.sin(math.asin(y / (math.sqrt((x**2) + (y**2))))), y
            )

        await drone.offboard.set_velocity_ned(
            sdk.VelocityNedYaw(2.0,2.0,up_speed,70)
        )


    async def test_takeoff(self, drone: System) -> None:
        logging.info("------------Test--------------")

        logging.info("Climbing")
        await drone.offboard.set_velocity_body(
                sdk.VelocityBodyYawspeed(0.0,0.0,-1.0,0.0)
        )

        await asyncio.sleep(10)

        logging.info("Going back down")
        await drone.offboard.set_velocity_body(
                sdk.VelocityBodyYawspeed(0.0,0.0,1.0,0.0)
        )

        await asyncio.sleep(5)

        logging.info("Hovering")
        await drone.offboard.set_velocity_body(
                sdk.VelocityBodyYawspeed(0.0,0.0,0.0,0.0)
        )

        await asyncio.sleep(3)

        logging.info("Landing Drone")
        await drone.action.land()
