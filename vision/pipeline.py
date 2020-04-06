"""
Takes information from the camera and gives it to vision
"""

import os
import sys

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

from vision.bounding_box import BoundingBox, ObjectType

import datetime
import json
from multiprocessing import Queue
from queue import Empty

from vision.obstacle.obstacle_finder import ObstacleFinder
from vision.common.import_params import import_params

from vision.module.location import ModuleLocation
from vision.module.get_module_depth import get_module_depth
#from vision.module.region_of_interest import region_of_interest
#from vision.module.module_orientation import get_module_orientation
from vision.module.module_bounding import getModuleBounds

class Pipeline:
    """
    This is a pipeline class that takes in a video, runs an obstacle detection algorithm,
    and updates the blobs to the environment class.

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
        prefix = 'vision' if os.path.isdir("vision") else ''

        #
        config_filename = os.path.join(prefix, 'obstacle', 'config.json')

        with open(config_filename, 'r') as config_file:
            config = json.load(config_file)

        self.obstacle_finder = ObstacleFinder(params=import_params(config))

        self.module_location = ModuleLocation()

    @property
    def picture(self):
        return next(self.camera)

    def run(self, prev_state):
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

        if state == 'early_laps':
            bboxes = self.obstacle_finder.find(color_image, depth_image)
        else:
            pass  # raise AttributeError(f"Unrecognized state: {state}")

        if state == 'module_detection':
            self.module_location.setImg(color_image, depth_image)
            
            center = self.module_location.getCenter()
            depth = get_module_depth(depth_image, center)
            #orientation = get_module_orientation(region_of_interest(depth_image, depth, center), center)
            
            box = BoundingBox(getModuleBounds(color_image, center, depth), ObjectType.MODULE)
            box.module_depth = depth # float
            #box.orientation = orientation # tuple
            
            bboxes.append(box)
        else:
            pass # raise AttributeError(f"Unrecognized state: {state}")

        ##
        self.vision_communication.put((datetime.datetime.now(), bboxes), self.PUT_TIMEOUT)

        # from vision.common.blob_plotter import plot_blobs
        # plot_blobs(self.obstacle_finder.keypoints, color_image)

        return state

def init_vision(vision_comm, flight_comm, video, runtime=100):
    """
    Alex, call this function - not run.
    """
    pipeline = Pipeline(vision_comm, flight_comm, video)

    prev_state = 'start'

    for _ in range(runtime):
        prev_state = pipeline.run(prev_state)


if __name__ == '__main__':
    from vision.camera.bag_file import BagFile

    vision_comm = Queue(100000)

    flight_comm = Queue()  # type('FlightCommunication', (object,), {'get_state': lambda: 'early_laps'})
    flight_comm.put('early_laps')

    video_file = sys.argv[1]
    video = BagFile(100, 100, 60, video_file)

    init_vision(vision_comm, flight_comm, video)

    from time import sleep
    sleep(1)

    vision_comm.close()
    flight_comm.close()
