import asyncio
import threading
from mavsdk import System
import mavsdk as sdk
from .states import STATES, State


class Comm:
    state: str = "start"


class StateMachine:
    def __init__(self, initial_state: State, drone: System) -> None:
        self.current_state: State = initial_state
        self.drone: System = drone

    async def run(self) -> None:
        while self.current_state:
            self.current_state: State = await self.current_state.run(self.drone)


SIM_ADDR: str = "udp://:14540"
CONTROLLER_ADDR: str = "serial:///dev/ttyUSB0"


async def print_flight_mode(drone: System) -> None:
    """ Prints the flight mode when it changes """

    previous_flight_mode: str = None

    async for flight_mode in drone.telemetry.flight_mode():
        if flight_mode is not previous_flight_mode:
            previous_flight_mode: str = flight_mode
            print(f"Flight mode: {flight_mode}")


async def observe_is_in_air(drone: System, comm) -> None:
    """ Monitors whether the drone is flying or not and
    returns after landing """

    was_in_air: bool = False

    async for is_in_air in drone.telemetry.in_air():
        if is_in_air:
            was_in_air: bool = is_in_air

        if was_in_air and not is_in_air:
            comm.set_state("exit")
            await asyncio.get_event_loop().shutdown_asyncgens()
            return


def flight(comm, sim: bool) -> None:
    asyncio.get_event_loop().run_until_complete(go(comm, sim))


async def go(comm, sim: bool) -> None:
    drone: System = await init_drone(sim)
    await start_flight(comm, drone)


async def init_drone(sim: bool) -> System:
    sys_addr: str = SIM_ADDR if sim else CONTROLLER_ADDR
    drone: System = System()
    await drone.connect(system_address=sys_addr)
    # Add lines to control takeoff height
    return drone


async def start_flight(comm, drone: System):
    asyncio.ensure_future(print_flight_mode(drone))
    termination_task = asyncio.ensure_future(observe_is_in_air(drone, comm))

    try:
        sm: StateMachine = StateMachine(STATES[comm.get_state()](), drone)
        await sm.run()
    except:
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

    comm.set_state("exit")

    await termination_task


if __name__ == "__main__":
    flight(Comm(), True)
