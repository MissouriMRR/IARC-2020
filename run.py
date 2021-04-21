#!/usr/bin/env python3
"""Main runnable file for the codebase"""

import argparse
import logging

from multiprocessing import Process, Queue
from multiprocessing.managers import BaseManager

from logger import init_logger, worker_configurer
from communication import Communication
from flight.flight import flight


def main() -> None:
    """
    Code that executes threads for flight

    Parameters:
        N/A
    Return:
        None
    Logging:
        To debug; Flag for if simulation is enabled
    """
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--simulation", help="using the simulator", action="store_true"
    )
    args = parser.parse_args()
    logging.debug("Simulation flag %s", "enabled" if args.simulation else "disabled")
    run_threads(args.simulation)


def init_flight(flight_args) -> Process:
    """
    Initialize flight process

    Parameters:
        flight_args: Arguments for args" in returned Process object
    Return:
        Process: multiprocessing object to hold attributes of current flight process
    Logging:
        N/A
    """
    return Process(target=flight, name="flight", args=flight_args)


def run_threads(sim: bool) -> None:
    """
    Begin flight processes and threads for code

    Parameters:
        sim (bool): Designates if current run is in a simulation
    Return:
        None
    Logging:
        To debug; returns start of flight process and its ID
        To error; flight process becomes terminated and needs a restart
        To info; marks the spawning of all processes
                 Marks moment of Ctrl-C exit
                 Existence of non-fatal attribute error
                 EOF error and justification
                 Error associated with a connection issue if it occurs
                 Marks end of processes
    """
    # Register Communication object to Base Manager
    BaseManager.register("Communication", Communication)
    # Create manager object
    manager: BaseManager = BaseManager()
    # Start manager
    manager.start()
    # Create Communication object from manager
    comm_obj = manager.Communication()

    log_queue: Queue = Queue(-1)
    logging_process = init_logger(log_queue)
    logging_process.start()

    worker_configurer(log_queue)

    # Create new processes
    logging.info("Spawning Processes")

    flight_args = (comm_obj, sim, log_queue, worker_configurer)
    flight_process: Process = init_flight(flight_args)
    # Start flight function
    flight_process.start()
    logging.debug("Flight process with id %d started", flight_process.pid)

    try:
        while comm_obj.get_state() != "final":
            # If the process is no longer alive,
            # (i.e. error has been raised in this case)
            # then create a new instance and start the new process
            # (i.e. restart the process)
            if flight_process.is_alive() is not True:
                logging.error("Flight process terminated, restarting")
                flight_process: Process = init_flight(flight_args)
                flight_process.start()
    except (KeyboardInterrupt, AttributeError) as error:
        # Ctrl-C was pressed
        # TODO send a message to the flight process to land instead of
        # basically overwriting the process
        try:
            logging.info("Ctrl-C Pressed, forcing drone to land")
            comm_obj.set_state("land")
            logging.info("Non-fatal AttributeError occurs, land still possible")
            flight_process: Process = init_flight(flight_args)
            flight_process.start()
        except EOFError:
            logging.info("Additional EOF error detected - lack of inputs on restart")
            comm_obj.set_state("hold")
            comm_obj.set_state("land")
            flight_process: Process = init_flight(flight_args)
            flight_process.start()
        except (TimeoutError, flight.DroneNotFoundError) as connection_issue:
            logging.info(connection_issue, ", cannot connect")

    # Join flight process before exiting function
    flight_process.join()

    logging.info("All processes ended, Goodbye!")
    logging_process.stop()


if __name__ == "__main__":
    # Run multiprocessing function
    try:
        main()
    except:
        logging.exception("Unfixable error detected")
