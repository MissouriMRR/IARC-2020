"""Takeoff procedure in which the drone goes straight up, for testing purposes"""

import logging
import mavsdk as sdk
from mavsdk import System

from .state import State
from .detect_module import DetectModule
from flight.utils.latlon import LatLon
from flight.utils.movement_controller import MovementController

from flight import config


class SimpleTakeoff(State):
    """The state that performs straight-vertical takeoff"""

    async def check_altitude(self, drone: System) -> bool:
        """
        Checks the altitude of the drone to make sure that we are at our target
        Parameters:
            drone(System): Our drone object
        """
        async for position in drone.telemetry.position():
            altitude: float = round(position.relative_altitude_m, 2)
            if altitude >= config.MAST_ALT:  # Test when aligned with mast
                return True

    async def run(self, drone: System):
        """Arms and takes off the drone"""

        # Sets takeoff location
        async for gps in drone.telemetry.position():
            config.takeoff_pos = LatLon(
                round(gps.latitude_deg, 8), round(gps.longitude_deg, 8)
            )
            break

        mover: MovementController = MovementController()
        await self._check_arm_or_arm(drone)  # Arms the drone if not armed
        logging.info("Taking off")
 
        # (NSm/s, EWm/s, DUm/s, Ydeg)
        await drone.offboard.set_velocity_ned(
            sdk.offboard.VelocityNedYaw(0.0, 0.0, 0.0, 0.0)
        )

        try:
            # Enable offboard mode, allowing for computer to control the drone
            await drone.offboard.start()
        except sdk.offboard.OffboardError:
            await drone.action.land()
            return

        await drone.offboard.set_velocity_ned(
            sdk.offboard.VelocityNedYaw(0.0, 0.0, -1.0, 0.0)
            # Sets teh velocity of the drone to be straight up
        )
        await self.check_altitude(drone)

        # After reaching altitude, attempt module detection
        return DetectModule(self.state_settings)
