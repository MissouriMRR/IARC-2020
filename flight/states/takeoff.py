"""The takeoff state"""
import asyncio
import logging
import mavsdk as sdk
from mavsdk import System

from .state import State
from .early_laps import EarlyLaps
from .approach_lap import ApproachLap

from flight import config


class Takeoff(State):
    """The state that takes off the drone"""

    async def run(self, drone: System) -> None:
        """Arms and takes off the drone"""
        await self._check_arm_or_arm(drone)  # Arms the drone if not armed
        logging.info("Taking off")
        # Takeoff command, goes to altitude specified in params
        await drone.action.takeoff()
        # waits for altitude to be close to the specified level
        await self.wait_alt(drone)

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

        return eval(config.RUN_LAPS)()  # Return the next state, RunLaps

    async def wait_alt(self, drone: System):
        """Checks to see if the drone is near the target altitude"""
        async for position in drone.telemetry.position():
            altitude: float = round(position.relative_altitude_m, 2)
            if altitude >= config.ALT_RANGE_MIN:
                return True
