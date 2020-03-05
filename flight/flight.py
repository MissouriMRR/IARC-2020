"""Launch code for flight state machine"""
import asyncio
import logging

from mavsdk import System
import mavsdk as sdk

from flight.states import STATES, State


class DroneNotFoundError(Exception):
    pass


class StateMachine:
    """
    Initializes the state machine and runs the states.

    Attributes:
        current_state (State): State that is currently being executed.
        drone (System): Our drone object; used for all flight functions.
    """

    def __init__(self, initial_state: State, drone: System) -> None:
        """
        The constructor for StateMachine class.

        Parameters:
            current_state (State): State that is currently being executed.
            drone (System): Our drone object; used for all flight functions.
        """
        self.current_state: State = initial_state
        self.drone: System = drone

    async def run(self) -> None:
        """
        Runs the state machine by infinitely replacing current_state until a
        state return None.
        """
        while self.current_state:
            self.current_state: State = await self.current_state.run(self.drone)


SIM_ADDR: str = "udp://:14540"  # Address to connect to the simulator
CONTROLLER_ADDR: str = "serial:///dev/ttyUSB0"  # Address to connect to a pixhawk board


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


async def wait_for_drone(drone: System) -> None:
    async for state in drone.core.connection_state():
        if state.is_connected:
            logging.info("Connected to drone with UUID %s", state.uuid)
            return


def flight(comm, sim: bool, log_queue, worker_configurer) -> None:
    """Starts the asyncronous event loop for the flight code"""
    worker_configurer(log_queue)
    logging.debug("Flight process started")
    asyncio.get_event_loop().run_until_complete(init_and_begin(comm, sim))


async def init_and_begin(comm, sim: bool) -> None:
    """Creates drone object and passes it to start_flight"""
    try:
        drone: System = await init_drone(sim)
        await start_flight(comm, drone)
    except DroneNotFoundError:
        logging.exception("Drone was not found")
        return
    except:
        logging.exception("Uncaught error occurred")
        return


async def init_drone(sim: bool) -> System:
    """Connects to the pixhawk or simulator and returns the drone"""
    sys_addr: str = SIM_ADDR if sim else CONTROLLER_ADDR
    drone: System = System()
    await drone.connect(system_address=sys_addr)
    logging.debug("Waiting for drone to connect...")
    try:
        await asyncio.wait_for(wait_for_drone(drone), timeout=5)
    except asyncio.TimeoutError:
        raise DroneNotFoundError()

    # Add lines to control takeoff height
    return drone


async def start_flight(comm, drone: System):
    """Creates the state machine and watches for exceptions"""
    # Continuously print flight mode changes
    asyncio.ensure_future(print_flight_mode(drone))
    # Will stop flight code if the drone lands
    termination_task = asyncio.ensure_future(observe_is_in_air(drone, comm))

    try:
        # Initialize the state machine at the current state
        state_machine: StateMachine = StateMachine(STATES[comm.get_state()](), drone)
        await state_machine.run()
    except Exception as err:
        print(str(err))
        try:
            await drone.offboard.set_position_ned(sdk.PositionNedYaw(0, 0, 0, 0))
            await drone.offboard.set_velocity_ned(sdk.VelocityNedYaw(0, 0, 0, 0))
            await drone.offboard.set_velocity_body(sdk.VelocityBodyYawspeed(0, 0, 0, 0))

            await asyncio.sleep(1)

            try:
                await drone.offboard.stop()
            except sdk.OffboardError as error:
                print(f"Stopping offboard mode failed with error code: {str(error)}")
                # Worried about what happens here
            await asyncio.sleep(1)
            print("-- Landing")
            await drone.action.land()
        except:
            print("No system")
            comm.set_state("final")
            return

    comm.set_state("final")

    await termination_task
