#!/usr/bin/env python3
"""Main runnable file for the codebase"""

import argparse
import logging
import time

from multiprocessing import Process, Queue
from multiprocessing.managers import BaseManager

from logger import init_logger, worker_configurer
from communication import Communication
from flight.flight import flight
from vision.camera.realsense import Realsense
from flight import config


def main() -> None:
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument(
        "-s", "--simulation", help="using the simulator", action="store_true"
    )
    args = parser.parse_args()
    logging.debug("Simulation flag %s", "enabled" if args.simulation else "disabled")
    run_threads(args.simulation)

def run_threads(sim: bool) -> None:

    log_queue: Queue = Queue(-1)
    logging_process = init_logger(log_queue)
    logging_process.start()

    worker_configurer(log_queue)

    # Create new processes
    logging.info("Spawning Processes")

    camera = Realsense(config.REALSENSE_SCREEN_WIDTH, config.REALSENSE_SCREEN_HEIGHT, config.REALSENSE_FRAMERATE)
    camera.display_in_window()

    time.sleep(10)

    logging.info("All processes ended, Goodbye!")
    logging_process.stop()


if __name__ == "__main__":
    # Run multiprocessing function
    try:
        main()
    except:
        logging.exception("Unfixable error detected")

