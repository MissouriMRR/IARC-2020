from mavsdk import System


class State:
    async def run(self, drone: System):
        assert 0, "run not implemented"

    async def _check_arm_or_arm(self, drone: System):
        print("Not armed -- Arming")
        await drone.action.arm()

