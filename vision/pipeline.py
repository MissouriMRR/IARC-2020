"""
Takes information from the camera and gives it to vision
"""

import os
import sys
import asyncio
import inspect
import time

start_time = time.time()

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

from vision.bounding_box import BoundingBox, ObjectType
from vision.camera import realsense

import datetime
import json
from multiprocessing import Queue
from queue import Empty

from vision.obstacle.obstacle_finder import ObstacleFinder
from vision.obstacle.obstacle_tracker import ObstacleTracker
from vision.common.import_params import import_params

from vision.text.detect_words import TextDetector

from vision.module.location import ModuleLocation
from vision.module.get_module_depth import get_module_depth
from vision.module.region_of_interest import region_of_interest
from vision.module.module_orientation import get_module_orientation
from vision.module.module_orientation import get_module_roll
from vision.module.module_bounding import get_module_bounds

from vision.failure_flags import ObstacleDetectionFlags
from vision.failure_flags import TextDetectionFlags
from vision.failure_flags import ModuleDetectionFlags


class Pipeline:
    """
    Pipeline to carry information from the cameras through
    the various vision algorithms out to flight.
    Parameters

    -------------
    vision_communication: multiprocessing Queue
        Interface to share vision information with flight.
    flight_communication: multiprocessing Queue
        Interface to recieve flight state information from flight.
    camera: Camera
        Camera to pull image from.
    """

    PUT_TIMEOUT = 1  # Expected time for results to be irrelevant.

    def __init__(self, vision_communication, flight_communication, camera):
        ##
        self.vision_communication = vision_communication
        self.flight_communication = flight_communication

        self.camera = camera.__iter__()

        ##
        prefix = "vision" if os.path.isdir("vision") else ""

        #
        config_filename = os.path.join(prefix, "obstacle", "config.json")

        with open(config_filename, "r") as config_file:
            config = json.load(config_file)

        self.obstacle_finder = ObstacleFinder(params=import_params(config))

        self.obstacle_tracker = ObstacleTracker()

        self.text_detector = TextDetector()

        self.module_location = ModuleLocation()

        self.vision_flags = []

    @property
    def picture(self):
        return next(self.camera)

    async def run(self, prev_state):
        """
        Process current camera frame.
        """
        ##
        depth_image, color_image = self.picture

        try:
            state = self.flight_communication.get_nowait()
        except Empty:
            state = prev_state

        ##
        bboxes = []

        flags = {}

        state = "module_detection"
        if state == "early_laps":  # navigation around the pylons
            flags = ObstacleDetectionFlags()

            try:
                bboxes = await self.obstacle_finder.find(color_image, depth_image)
                await self.obstacle_tracker.update(bboxes)
            except:
                flags.obstacle_finder = False

            try:
                bboxes = await self.obstacle_tracker.getPersistentObstacles()
            except:
                flags.obstacle_tracker = False

        elif state == "text_detection":  # approaching mast
            flags = TextDetectionFlags()

            try:
                bboxes = await self.text_detector.detect_russian_word(
                    color_image, depth_image
                )
            except:
                flags.detect_russian_word = False

        elif state == "module_detection":  # locating module
            flags = ModuleDetectionFlags()
            try:
                await self.module_location.setImg(color_image, depth_image)
            except:
                flags.setImg = False

            try:
                inFrame = await self.module_location.isInFrame()
            except:
                inFrame = False
                flags.isInFrame = False

            # only do more calculation if module is in the image
            if inFrame:
                try:
                    center = await (
                        self.module_location.getCenter()
                    )  # center of module in image
                except:
                    flags.getCenter = False

                try:
                    depth = await get_module_depth(
                        depth_image, center
                    )  # depth of center of module
                except:
                    flags.get_module_depth = False

                try:
                    egion = await region_of_interest(
                        depth_image, depth, center
                    )  # depth image sliced on underestimate bounds
                except:
                    flags.region_of_interest = False

                try:
                    orientation = await get_module_orientation(
                        region
                    )  # x and y tilt of module
                except:
                    flags.get_module_orientation = False

                try:
                    bounds = await getModuleBounds(
                        color_image, center, depth
                    )  # overestimate of bounds
                except:
                    flags.getModuleBounds = False

                try:
                    roll = await get_module_roll(
                        color_image[
                            bounds[0][1] : bounds[3][1], bounds[0][0] : bounds[2][0], :
                        ]
                    )  # roll of module
                except:
                    flags.get_module_roll = False

                # construct boundingbox for the module
                box = await BoundingBox(bounds, ObjectType.MODULE)
                box.module_depth = depth  # float
                box.orientation = orientation + (roll,)  # x, y, z tilt
                await bboxes.append(box)

        else:
            pass  # raise AttributeError(f"Unrecognized state: {state}")

        self.vision_flags.append(flags)

        ##
        self.vision_communication.put(
            (datetime.datetime.now(), bboxes), self.PUT_TIMEOUT
        )

        # uncomment to visualize blobs
        # from vision.common.blob_plotter import plot_blobs
        # plot_blobs(self.obstacle_finder.keypoints, color_image)
        return state


async def init_vision(vision_comm, flight_comm, video, runtime=100):
    """
    Alex, call this function - not run.
    """
    pipeline = Pipeline(vision_comm, flight_comm, video)

    state = "start"

    for _ in range(runtime):
        state = pipeline.run(state)
        asyncio.gather(state)

    for flag in pipeline.vision_flags:
        print(flag)


if __name__ == "__main__":
    from vision.camera.bag_file import BagFile

    vision_comm = Queue(100000)

    flight_comm = (
        Queue()
    )  # type('FlightCommunication', (object,), {'get_state': lambda: 'early_laps'})
    flight_comm.put("early_laps")

    video_file = sys.argv[1]
    video = BagFile(100, 100, 60, video_file)

    asyncio.run(init_vision(vision_comm, flight_comm, video))

    from time import sleep

    sleep(2)  # allow queue to close

    # print(inspect.iscoroutinefunction(init_vision))
    # print(inspect.iscoroutinefunction(Pipeline.__init__))
    # print(inspect.iscoroutinefunction(Pipeline.picture))
    # print(inspect.iscoroutinefunction(Pipeline.run))

    vision_comm.close()
    flight_comm.close()
    print("--- %s seconds ---" % (time.time() - start_time))
