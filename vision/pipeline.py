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
    def __init__(self, env, obstacle_finder, config, alg_time=98):
        if not isinstance(env, Environment):
            raise ValueError(f"Argument env should be type Environment, got {type(env)}")
        if type(alg_time) is not int:
            raise ValueError(f"Argument alg_time should be type int, got {type(alg_time)}")
        if not isinstance(obstacle_finder, ObstacleFinder):
            raise ValueError(f"Argument obstacle_finder should be type ObstacleFinder, got {type(obstacle_finder)}")
        self.env = env
        self.obstacle_finder = obstacle_finder
        self.config = config
        self.alg_time = alg_time

    def run_algorithm(self, video_file):
        """
        Method that takes the given video file and environment, and updates the
        environment with detected blobs.

        Parameters
        ----------
        vid_file: BagFile
            The .bag video file represented by a BagFile object
        """

        if not isinstance(video_file, BagFile):
            raise ValueError(f"Argument video_file should be type BagFile, got {type(video_file)}")

        for i, (depth_image, color_image) in enumerate(video_file):
            if i == self.alg_time:
                break

            bboxes = self.obstacle_finder.find(color_image, depth_image)
            self.env.update(bboxes)

            plot_blobs(self.obstacle_finder.keypoints, color_image)


if __name__ == '__main__':
    from vision.interface import Environment

    prefix = 'vision' if os.path.isdir("vision") else ''
    config_filename = os.path.join(prefix, 'obstacle', 'config.json')
    env = Environment()

    with open(config_filename, 'r') as config_file:
        config = json.load(config_file)

    obstacle_finder = ObstacleFinder(params=import_params(config))

    video_file = sys.argv[1]
    video = BagFile(100, 100, 60, video_file)

    pipeline = Pipeline(env, obstacle_finder, config)
    pipeline.run_algorithm(video)
