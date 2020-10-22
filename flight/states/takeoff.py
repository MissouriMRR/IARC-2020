"""The takeoff state"""
import asyncio
import logging
import mavsdk as sdk
from mavsdk import System

from .state import State
from .early_laps import EarlyLaps

from flight import config


class Takeoff(State):
    """The state that takes off the drone"""

    async def run(self, drone: System) -> None:
        """Arms and takes off the drone"""
        await self._check_arm_or_arm(drone)  # Arms the drone if not armed
        logging.info("Taking off")

        # Setting set points for the next 3 lines (used to basically set drone center)
        # (NSm, EWm, DUm, Ydeg)
        await drone.offboard.set_position_ned(
            sdk.offboard.PositionNedYaw(0.0, 0.0, 0.0, 0.0)
        )

        # (NSm/s, EWm/s, DUm/s, Ydeg)
        await drone.offboard.set_velocity_ned(
            sdk.offboard.VelocityNedYaw(0.0, 0.0, 0.0, 0.0)
        )

        # (FBm/s, RLm/s, DUm/s, Yspdeg/s)
        await drone.offboard.set_velocity_body(
            sdk.offboard.VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
        )

        try:
            # Enable offboard mode, allowing for computer to control the drone
            await drone.offboard.start()
        except sdk.OffboardError:
            await drone.action.land()
            return

        await self.takeoff(drone, 1.0)
        #Takes off vertically until a desired altitude
        #Then moves onto EarlyLaps, were the wait_pos function moves the drone towards the first pylon
        return EarlyLaps()  # Return the next state, RunLaps

    async def takeoff(self, drone: (System), alt):
        """Takes off vertically to a height defined by alt"""

        await drone.offboard.set_velocity_ned(
            sdk.offboard.VelocityNedYaw(0.0, 0.0, -1.0, 0.0)
            #Sets the velocity of the drone to be straight up
        )
        await self.wait_alt(drone, alt)
        #Waits until a desired altitude is reached, before moving on to EarlyLaps

        return

    async def wait_alt(self, drone: System, alt):
        """Checks to see if the drone is near the target altitude"""
        async for position in drone.telemetry.position():
            altitude: float = round(position.relative_altitude_m, 2)
            if altitude >= alt:
                return True
