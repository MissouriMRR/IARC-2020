"""
Takes information from the camera and gives it to vision
"""

import os
import json
from vision.camera.read_bag import ReadBag
from vision.obstacle.obstacle_finder import ObstacleFinder
from vision.util.import_params import import_params
from vision.util.obstacle_plotter import plot_obstacles


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
    def __init__(self, vid_file, env, alg_time=98):
        self.vid_file = vid_file
        self.env = env
        self.alg_time = alg_time

    def run_algorithm(self):
        """
        Method that takes the given video file and environment, and updates the
        environment with detected blobs.
        """
        for i, (depth_image, color_image) in enumerate(ReadBag(self.vid_file)):
            if i == self.alg_time:
                break
            obstacle_finder = ObstacleFinder(params=import_params(config))
            bboxes = obstacle_finder.find(color_image)
            env.update(bboxes)

            plot_obstacles(obstacle_finder.keypoints, color_image)


if __name__ == '__main__':
    from vision.interface import Environment

    prefix = 'vision' if os.path.isdir("vision") else ''
    config_filename = os.path.join(prefix, 'obstacle', 'config.json')
    env = Environment()

    with open(config_filename, 'r') as config_file:
        config = json.load(config_file)

    video_file_name = os.path.join('vision_videos', 'module', 'sampleFrames.bag')

    the_pipe = Pipeline(video_file_name, env)
    the_pipe.run_algorithm()
