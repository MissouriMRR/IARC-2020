"""State to land the drone"""
import asyncio
import logging
import mavsdk as sdk

from flight import config

from mavsdk import System

from .state import State
from .final import Final


class Land(State):
    """
    Contains the functions needed to halt and land the drone, and turns off
    offboard
    """

    async def manual_land(self, drone: System):
        # Lands the drone using manual velocity values
        logging.info("Landing the drone...")
        async for position in drone.telemetry.position():
            current_altitude: float = round(position.relative_altitude_m, 3)
            if current_altitude > 1.0:
                # 0.7 m/s is default velocity used in drone.action.land() command, can be changed if necessary
                await drone.offboard.set_velocity_body(
                    sdk.offboard.VelocityBodyYawspeed(0.0, 0.0, 0.7, 0.0)
                )
            elif 1.0 > current_altitude > 0.1:
                await drone.offboard.set_velocity_body(
                    sdk.offboard.VelocityBodyYawspeed(0.0, 0.0, 0.35, 0.0)
                )
            else:
                await drone.offboard.set_velocity_body(
                    sdk.offboard.VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
                )
                return

    async def run(self, drone: System) -> State:
        """
        Stops the drone by setting all movements to 0, then move to land
        mode
        """
        await drone.offboard.set_position_ned(sdk.offboard.PositionNedYaw(0, 0, 0, 0))
        await drone.offboard.set_velocity_ned(sdk.offboard.VelocityNedYaw(0, 0, 0, 0))
        await drone.offboard.set_velocity_body(
            sdk.offboard.VelocityBodyYawspeed(0, 0, 0, 0)
        )

        await asyncio.sleep(config.THINK_FOR_S)
        await self.manual_land(drone)

        try:
            await drone.offboard.stop()
        except sdk.offboard.OffboardError as error:
            logging.exception(
                "Stopping offboard mode failed with error code: %s", str(error)
            )
        logging.info("Disarming the drone...")
        await drone.action.kill()
        return Final()
