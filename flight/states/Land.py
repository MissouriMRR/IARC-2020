import asyncio
from mavsdk import System
import mavsdk as sdk
from .State import State
from .Final import Final


class Land(State):
    async def run(self, drone: System) -> State:
        await drone.offboard.set_position_ned(sdk.PositionNedYaw(0, 0, 0, 0))
        await drone.offboard.set_velocity_ned(sdk.VelocityNedYaw(0, 0, 0, 0))
        await drone.offboard.set_velocity_body(sdk.VelocityBodyYawspeed(0, 0, 0, 0))

        await asyncio.sleep(1)

        try:
            await drone.offboard.stop()
        except sdk.OffboardError as error:
            print(
                f"Stopping offboard mode failed with error code: {error._result.result}"
            )
            # Worried about what happens here

        await asyncio.sleep(1)

        print("-- Landing")
        await drone.action.land()
        return Final()
