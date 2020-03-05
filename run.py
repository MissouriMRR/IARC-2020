#!/usr/bin/env python3

from multiprocessing import Process
from multiprocessing.managers import BaseManager
from communication import Communication
from flight.flight import flight
import argparse


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--simulation", help="using the simulator", action="store_true"
    )
    args = parser.parse_args()

    # Input loop
    # start will start the run_threads function to start flight and vision
    # exit will do nothing and simpy exit the program

    select = input('>>> Type \'start\' to start the drone, or \'exit\' to exit.')

    while select != 'start' and select != 'exit':
        select = input('>>> Type \'start\' to start the drone, or \'exit\' to exit.')

    # If the user input is start, start run_threads to start flight and vision
    if select == 'start':
        run_threads(args.simulation)


def run_threads(sim: bool) -> None:

    # Register Communication object to Base Manager
    BaseManager.register("Communication", Communication)
    # Create manager object
    manager = BaseManager()
    # Start manager
    manager.start()
    # Create Communication object from manager
    comm_obj = manager.Communication()

    comm_obj.set_state('takeoff')

    # Create new processes
    print("-----Begin Processes-----")
    f = Process(target=flight, args=(comm_obj, sim,))

    # Start flight function
    f.start()

    try:
        while comm_obj.get_state() != "exit":

            # If the process is no longer alive,
            # (i.e. error has been raised in this case)
            # then create a new instance and start the new process
            # (i.e. restart the process)
            if f.is_alive() == False:
                print("===========Restarting Flight===========")
                f = Process(target=flight, args=(comm_obj, sim,))
                f.start()
    except KeyboardInterrupt:
        # Ctrl-C was pressed
        comm_obj.set_state("land")
        print("===========Forcing Drone to Stop===========")
        f = Process(target=flight, args=(comm_obj, sim,))
        f.start()

    # Join flight process before exiting function
    f.join()

    print("----End of Processes----")


if __name__ == "__main__":
    # Run multiprocessing function
    main()
