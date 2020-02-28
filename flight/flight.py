import asyncio
import threading
from mavsdk import System


class Comm:
    state = "start"


class State:
    def run(self, drone: System):
        assert 0, "run not implemented"


class Takeoff(State):
    def run(self, drone: System) -> None:
        print("taking off")


class Start(State):
    def run(self, drone: System) -> State:
        print("Start")
        input("Press enter when ready")
        return STATES["takeoff"]


STATES = {"start": Start(), "takeoff": Takeoff(), "land": None, "final": None}


class StateMachine:
    def __init__(self, initial_state, drone):
        self.current_state: State = initial_state
        self.drone = drone
        self.run()

    def run(self):
        while self.current_state:
            self.current_state: State = self.current_state.run(self.drone)


SIM_ADDR: str = "udp://:14540"
CONTROLLER_ADDR: str = "serial:///dev/ttyUSB0/"


async def print_flight_mode(drone):
    """ Prints the flight mode when it changes """

    previous_flight_mode = None

    async for flight_mode in drone.telemetry.flight_mode():
        if flight_mode is not previous_flight_mode:
            previous_flight_mode = flight_mode
            print(f"Flight mode: {flight_mode}")


async def observe_is_in_air(drone):
    """ Monitors whether the drone is flying or not and
    returns after landing """

    was_in_air = False

    async for is_in_air in drone.telemetry.in_air():
        if is_in_air:
            was_in_air = is_in_air

        if was_in_air and not is_in_air:
            await asyncio.get_event_loop().shutdown_asyncgens()
            print("-- Land")
            return


def flight(comm: Comm, sim: bool):
    drone: System = init_drone(sim)
    asyncio.get_event_loop().run_until_complete(start_flight(comm, drone))


def init_drone(sim: bool) -> System:
    sys_addr = SIM_ADDR if sim else CONTROLLER_ADDR
    drone: System = System()
    await drone.connect(system_address=sys_addr)
    # Add lines to control takeoff height
    return drone


async def start_flight(comm: Comm, drone: System):
    asyncio.ensure_future(print_flight_mode(drone))
    termination_task = asyncio.ensure_future(observe_is_in_air(drone))

    StateMachine(STATES[comm.state], drone)

    await termination_task


if __name__ == "__main__":
    await flight(Comm(), True)
