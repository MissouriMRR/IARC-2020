"""
Takes information from the camera and gives it to vision
"""

import os
import sys

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import json

from vision.camera.template import Camera
from vision.camera.bag_file import BagFile
from vision.obstacle.obstacle_finder import ObstacleFinder
from vision.common.blob_plotter import plot_blobs
from vision.common.import_params import import_params


class Pipeline:
    """
    This is a pipeline class that takes in a video, runs an obstacle detection algorithm,
    and updates the blobs to the environment class.

    Parameters
    -------------
    env: Environment
        The environment interface that is used by flight code.
        The pipeline updates the interface.

    alg_time: int
        An integer value that corresponds to how long the video loops.
    """
    def __init__(self, env, camera):
        if not isinstance(env, Environment):
            raise ValueError(f"Argument env should be type Environment, got {type(env)}")
        if not isinstance(camera, Camera):
            raise ValueError(f"Argument env should be type Camera, got {type(camera)}")

        ##
        self.env = env
        self.camera = camera.__iter__()

        ##
        prefix = 'vision' if os.path.isdir("vision") else ''
        
        #
        config_filename = os.path.join(prefix, 'obstacle', 'config.json')

        with open(config_filename, 'r') as config_file:
            config = json.load(config_file)

        self.obstacle_finder = ObstacleFinder(params=import_params(config))

    @property
    def picture(self):
        return next(self.camera)

    def run(self):
        """
        Method that takes the given video file and environment, and updates the
        environment with detected blobs.

        Parameters
        ----------
        vid_file: BagFile
            The .bag video file represented by a BagFile object
        """
        depth_image, color_image = self.picture

        bboxes = self.obstacle_finder.find(color_image, depth_image)
        self.env.update(bboxes)

        plot_blobs(self.obstacle_finder.keypoints, color_image)


if __name__ == '__main__':
    from vision.interface import Environment

    env = Environment()

    video_file = sys.argv[1]
    video = BagFile(100, 100, 60, video_file)

    pipeline = Pipeline(env, video)

    for _ in range(100):
        pipeline.run()
