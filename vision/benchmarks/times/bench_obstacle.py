"""
Utility to measure performance of obstacle detector.

Parameter Defaults
------------------
Resolution = (1280, 720)
Noise SD = 0
N Objects = 0
Type = circle
Radius = 100
"""
import os, sys
parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import json
import numpy as np
import cv2

import common

from vision.obstacle.obstacle_finder import ObstacleFinder
from vision.util.import_params import import_params


class TimeObstacle:
    """
    Timing ObstacleFinder methods.
    """
    DEFAULT_DIMS = (1280, 720)
    DEFAULT_RADIUS = 100

    def setup(self):
        """
        Configure blob detector and initialize images.
        """
        ## Generate images
        self.PARAMETERS = {}

        self.PARAMETERS.update(common.blank_dimensions())

        base_color, base_depth = common.blank_dimensions(self.DEFAULT_DIMS)

        #
        for radius in [25, 50, 100, 250]:
            color_image, depth_image = np.copy(base_color), np.copy(base_depth)

            cv2.circle(color_image, (640, 360), radius, (255, 255, 255), thickness=-1)
            cv2.circle(depth_image, (640, 360), radius, (255), thickness=-1)

            self.PARAMETERS.update({f'radius={radius}': (color_image, depth_image)})

        # One to each corner
        for n_obj in range(4):
            color_image, depth_image = np.copy(base_color), np.copy(base_depth)

            for location in [(320, 180), (320, 540), (960, 180), (960, 540)][:n_obj]:
                cv2.circle(color_image, location, self.DEFAULT_RADIUS, (255, 255, 255), thickness=-1)
                cv2.circle(depth_image, location, self.DEFAULT_RADIUS, (255), thickness=-1)

            self.PARAMETERS.update({f'n_obj={n_obj}': (color_image, depth_image)})

        # On default noise specturm
        for title, (color_image, depth_image) in common.noise().items():
            cv2.circle(color_image, (640, 360), self.DEFAULT_RADIUS, (255, 255, 255), thickness=-1)
            cv2.circle(depth_image, (640, 360), self.DEFAULT_RADIUS, (255), thickness=-1)

            self.PARAMETERS.update({f'{title} single': (color_image, depth_image)})

        ## Read current params & setup obstacle detector
        prefix = '' if os.path.isdir("times") else '..'

        config_filename = os.path.join(prefix, '..', 'obstacle', 'config.json')

        with open(config_filename, 'r') as config_file:
            config = json.load(config_file)

        self.blob_finder = ObstacleFinder(params=import_params(config))

    def time_find(self, color_image, depth_image):
        """
        Time the ObstacleFinder.find function.
        """
        self.blob_finder.find(color_image, depth_image)
