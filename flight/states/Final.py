from .State import State
from mavsdk import System


class Final(State):
    async def run(self, drone: System) -> None:
        print("Final")
