"""After arriving at the mast, detect the module"""
import mavsdk as sdk
from mavsdk import System

from multiprocessing import Queue
import logging
import asyncio

from flight import config
from .state import State
from .land import Land

from vision.camera.realsense import Realsense
from vision.pipeline import Pipeline


class DetectModule(State):
    """Detects the module using computer vision"""

    async def run(self, drone: System):
        """Detects the module using computer vision"""
        if self.state_settings.detect_module:
            # Stop moving
            await drone.offboard.set_velocity_ned(
                sdk.offboard.VelocityNedYaw(0.0, 0.0, 0.0, 0.0)
            )

            logging.info("Starting module detection...")

            logging.info("Initiating Realsense")
            camera: Realsense = Realsense(0, 0, config.REALSENSE_FRAMERATE)
            camera.display_in_window()

            logging.info("Starting vision pipeline")
            pipeline: Pipeline = Pipeline(Queue(), Queue(), camera)

            logging.info("Running module detection")
            pipeline.run("module_detection")

            await asyncio.sleep(10)

            logging.info("Detection results:")
            logging.info(pipeline.vision_communication)

            await asyncio.sleep(5)

        return Land(self.state_settings)
