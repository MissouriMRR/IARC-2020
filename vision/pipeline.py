"""
Takes information from the camera and gives it to vision
"""

import os
import json
from camera.bag_file import BagFile
from obstacle.obstacle_finder import ObstacleFinder
from common import import_params


class Pipeline:
    """
    This is a pipeline class that takes in a video, runs a obstacle detection algorithm,
    and updates the blobs to the environment class.

    Parameters
    -------------
    vid_file: str
        Filename of .bag file that the algorithm can act upon.

    env: Environment
        The environment interface that is used by flight code.
        The pipeline updates the interface.

    alg_time: int
        An integer value that corresponds to how long the video loops.
    """
    def __init__(self, vid_file, env, config, alg_time=98):
        self.vid_file = vid_file
        self.env = env
        self.alg_time = alg_time
        self.config = config

    def run_algorithm(self):
        """
        Method that takes the given video file and environment, and updates the
        environment with detected blobs.
        """
        for i, (depth_image, color_image) in enumerate(BagFile(0, 0, 0, self.vid_file)):
            if i == self.alg_time:
                break
            obstacle_finder = ObstacleFinder(params=import_params.import_params(self.config))
            bboxes = obstacle_finder.find(color_image, depth_image)
            self.env.update(bboxes)

            #from util.obstacle_plotter import plot_obstacles
            #plot_obstacles(obstacle_finder.keypoints, color_image)


if __name__ == '__main__':
    from vision.interface import Environment

    prefix = 'vision' if os.path.isdir("vision") else ''
    config_filename = os.path.join(prefix, 'obstacle', 'config.json')
    env = Environment()

    with open(config_filename, 'r') as config_file:
        config = json.load(config_file)

    video_file_name = os.path.join('vision_videos', 'module', 'sampleFrames.bag')

    the_pipe = Pipeline(video_file_name, env, config)
    the_pipe.run_algorithm()
