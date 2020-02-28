"""
Utility to measure performance of obstacle detector.
"""
import os, sys
parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import json
import cv2

import common

from vision.obstacle.obstacle_finder import ObstacleFinder
from vision.util.import_params import import_params


class TimeObstacle:
    """
    Timing ObstacleFinder methods.
    """
    def setup(self):
        """
        Configure blob detector and initialize images.
        """
        prefix = '' if os.path.isdir("times") else '..'

        ## Load images
        img_folder = os.path.join(prefix, '..', 'vision_images', 'obstacle')

        self.PARAMETERS = {}

        self.PARAMETERS.update(common.blank_dimensions())

        """
        for filename in os.listdir(img_folder):
            if filename[-4:] not in ['.png', '.jpg']:
                continue

            img_path = os.path.join(img_folder, os.fsdecode(filename))

            image = cv2.imread(img_path)

            self.PARAMETERS.update({filename: [image, None]})
        """

        ## Read current params & setup obstacle detector
        config_filename = os.path.join(prefix, '..', 'obstacle', 'config.json')

        with open(config_filename, 'r') as config_file:
            config = json.load(config_file)

        self.blob_finder = ObstacleFinder(params=import_params(config))

    def time_find(self, color_image, depth_image):
        """
        Time the ObstacleFinder.find function.
        """
        self.blob_finder.find(color_image, depth_image)
