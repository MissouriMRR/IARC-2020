from mavsdk import System
from .Final import Final


class Land(State):
    async def run(self) -> State:
        try:
            await self.drone.offboard.stop()
        except sdk.OffboardError as error:
            print(
                f"Stopping offboard mode failed with error code: {error._result.result}"
            )
            # Worried about what happens here

        await asyncio.sleep(1)

        print("-- Landing")
        await self.drone.action.land()
