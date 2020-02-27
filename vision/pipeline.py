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
from vision.blob.blobfind import import_params, BlobFinder
from vision.util.blob_plotter import plot_blobs


class Pipeline:
    """
    This is a pipeline class that takes in a video, runs a blob detection algorithm,
    and updates the blobs to the environment class.

    Parameters
    -------------
    env: Environment
        The environment interface that is used by flight code. 
        The pipeline updates the interface.

    alg_time: int
        An integer value that corresponds to how long the video loops.
    """
    def __init__(self, env, alg_time=98):
        if not isinstance(env, Environment):
            raise ValueError(f"Argument env should be type Environment, got {type(env)}")
        self.env = env
        if type(alg_time) is not int:
            raise ValueError(f"Argument alg_time should be type int, got {type(alg_time)}")
        self.alg_time = alg_time

    def run_algorithm(self, vid_file):
        """
        Method that takes the given video file and environment, and updates the
        environment with detected blobs.

        Parameters
        ----------
        vid_file: BagFile
            The .bag video file represented by a BagFile object
        """

        if not isinstance(vid_file, BagFile):
            raise ValueError(f"Argument vid_file should type BagFile, got {type(vid_file)}")

        for i, (depth_image, color_image) in enumerate(vid_file):
            if i == self.alg_time:
                break
            blob_finder = BlobFinder(params=import_params(config))
            bboxes = blob_finder.find(color_image)
            env.update(bboxes)

            plot_blobs(blob_finder.keypoints, color_image)


if __name__ == '__main__':
    from vision.interface import Environment

    prefix = 'vision' if os.path.isdir("vision") else ''
    config_filename = os.path.join(prefix, 'blob', 'config.json')
    env = Environment()

    with open(config_filename, 'r') as config_file:
        config = json.load(config_file)

    module_video = os.path.join('vision_videos', 'module', 'brick-left-right-tilt.bag')
    sample_video = os.path.join('vision_videos', 'module', 'sampleFrames.bag')
    module_video_file = BagFile(100, 100, 60, module_video)
    sample_video_file = BagFile(100, 100, 60, sample_video)

    pipeline = Pipeline(env)
    pipeline.run_algorithm(sample_video_file)
