from .Takeoff import Takeoff
from .State import State
from mavsdk import System


class Start(State):
    async def run(self, drone: System) -> State:
        print("Start")
        return Takeoff()
