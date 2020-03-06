#!/usr/bin/env python3

from multiprocessing import Process, Queue
from multiprocessing.managers import BaseManager
from communication import Communication
from flight.flight import flight
from vision.camera.realsense import Realsense
import argparse

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--simulation", help="using the simulator", action="store_true"
    )
    args = parser.parse_args()
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

    # Create Flight and vision queues
    flight_queue = Queue()
    vision_queue = Queue()

    # Create Camera object
    camera = Realsense(1080, 720, 30)

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
