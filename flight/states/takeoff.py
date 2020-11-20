"""The takeoff state"""
import asyncio
import logging
import mavsdk as sdk
from mavsdk import System

from .state import State
from .early_laps import EarlyLaps
from flight.utils.latlon import LatLon
from flight.utils.movement_controller import MovementController

from flight import config


class Takeoff(State):
    """The state that takes off the drone"""

    async def run(self, drone: System) -> None:
        """Sets takeoff location"""
        async for gps in drone.telemetry.position():
            takeoff_lat: float = round(gps.latitude_deg, 8)
            takeoff_lon: float = round(gps.longitude_deg, 8)
            takeoff_position = LatLon(takeoff_lat, takeoff_lon)
            config.takeoff_pos = takeoff_position
            break
        """Arms and takes off the drone"""
        mover: MovementController = MovementController()
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
        except sdk.offboard.OffboardError:
            await drone.action.land()
            return

        await mover.takeoff(drone)
        # Takes off vertically until a desired altitude constant TAKEOFF_ALT
        # Then moves onto EarlyLaps, were the wait_pos function moves the drone towards the first pylon
        return EarlyLaps()  # Return the next state, EarlyLaps
