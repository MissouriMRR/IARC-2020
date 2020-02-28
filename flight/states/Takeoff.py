import asyncio
from mavsdk import System
import mavsdk as sdk
from .State import State
from .RunLaps import RunLaps


class Takeoff(State):
    async def run(self, drone: System) -> None:
        await self._check_arm_or_arm(drone)
        print("taking off")
        print("-- Taking off")
        await drone.action.takeoff()
        alt_wait = asyncio.ensure_future(self.wait_alt(drone))
        await alt_wait
        alt_wait.cancel()

        # (NSm, EWm, DUm, Ydeg)
        await drone.offboard.set_position_ned(sdk.PositionNedYaw(0.0, 0.0, 0.0, 0.0))

        # (NSm/s, EWm/s, DUm/s, Ydeg)
        await drone.offboard.set_velocity_ned(sdk.VelocityNedYaw(0.0, 0.0, 0.0, 0.0))

        # (FBm/s, RLm/s, DUm/s, Yspdeg/s)
        await drone.offboard.set_velocity_body(
            sdk.VelocityBodyYawspeed(0.0, 0.0, 0.0, 0.0)
        )

        try:
            await drone.offboard.start()
        except sdk.OffboardError:
            await drone.action.land()
            return

        return RunLaps()

    async def wait_alt(self, drone: System):
        previous_altitude = None
        async for position in drone.telemetry.position():
            altitude = round(position.relative_altitude_m, 2)
            if altitude >= 2:
                return True
