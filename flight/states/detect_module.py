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


async def arange(count):
    """Asynchronous range"""
    for i in range(count):
        yield i


class DetectModule(State):
    """Detects the module using computer vision"""

    async def run(self, drone: System):
        """Detects the module using computer vision"""
        if self.state_settings.detect_module:
            # Stop moving
            await drone.offboard.set_velocity_ned(
                sdk.offboard.VelocityNedYaw(0.0, 0.0, 0.0, 0.0)
            )

            logging.info("Initializing Realsense...")
            camera: Realsense = Realsense(0, 0, config.REALSENSE_FRAMERATE)
            logging.info("Realsense set up successfully")

            logging.info("Starting vision pipeline...")
            pipeline: Pipeline = Pipeline(Queue(), Queue(), camera)
            logging.info("Pipeline set up successfully")

            # Run module detection if set in the state settings
            if self.state_settings.vision_test_type == "module":

                logging.info("Preparing to run module detection...")
                pipeline.run("module_detection")
                logging.info("Running module detection")

                await asyncio.sleep(5)

                logging.info("Module detection results:")
                async for i in arange(10):
                    logging.info(pipeline.vision_communication.get())
                    await asyncio.sleep(0.3)

                await asyncio.sleep(5)
            # Run mast text detection if set in the state settings
            elif self.state_settings.vision_test_type == "text":

                logging.info("Preparing to run mast text detection...")
                pipeline.run("text_detection")
                logging.info("Running text detection")

                await asyncio.sleep(5)

                logging.info("Text detection results:")
                logging.info(pipeline.vision_communication.get())

                await asyncio.sleep(5)
            # Otherwise, no test was set
            else:
                if self.state_settings.vision_test_type == "":
                    logging.warning("Provided vision test is empty")
                else:
                    logging.warning(
                        f"Invalid vision test specified: {self.state_settings.vision_test_type}"
                    )

        logging.info("DetectModule state finished")
        return Land(self.state_settings)
