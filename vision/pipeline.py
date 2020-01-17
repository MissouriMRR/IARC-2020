"""
Takes information from the camera and gives it to vision
"""

import os
import json
from vision.realsense.read_bag import ReadBag
from vision.blob.blobfind import import_params, BlobFinder
from vision.util.blob_plotter import plot_blobs


class Pipeline:

    def __init__(self, vid_file, env):
        self.vid_file = vid_file
        self.env = env

    def run_algorithm(self):

        for i, (depth_image, color_image) in enumerate(ReadBag(self.vid_file)):
            if i == 98:
                break
            blob_finder = BlobFinder(color_image, params=import_params(config))
            bboxes = blob_finder.find()
            env.update(bboxes)

            plot_blobs(blob_finder.keypoints, color_image)


if __name__ == '__main__':

    from vision.interface import Environment

    prefix = 'vision' if os.path.isdir("vision") else ''
    config_filename = os.path.join(prefix, 'blob', 'config.json')
    env = Environment()

    with open(config_filename, 'r') as config_file:
        config = json.load(config_file)

    video_file_name = os.path.join('vision_videos', 'module', 'sampleFrames.bag')

    the_pipe = Pipeline(video_file_name, env)
    the_pipe.run_algorithm()
