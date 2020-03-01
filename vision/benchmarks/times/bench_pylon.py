"""
Runs through images and determines which have the pylon.

Parameter Defaults
------------------
Resolution = (1280, 720)
Noise SD = 0
N Objects = 0
Thickness = 10
"""
import os, sys
parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import numpy as np
import cv2

import common

from vision.pylon.detect_pylon import detect_red


class TimePylon:
    """
    Timing all functionality of pylon project.
    """
    DEFAULT_DIMS = (1280, 720)
    DEFAULT_THICKNESS = 10

    def setup(self):
        """
        Load images.
        """
        ## Generate images
        self.PARAMETERS = {}

        self.PARAMETERS.update(common.blank_dimensions())

        base_color, base_depth = common.blank_dimensions(self.DEFAULT_DIMS)

        #
        for thickness in [3, 5, 10, 20]:
            color_image, depth_image = np.copy(base_color), np.copy(base_depth)

            cv2.line(color_image, (360, 0), (360, 1280), (255, 0, 0), thickness)
            cv2.line(depth_image, (360, 0), (360, 1280), (255), thickness)

            self.PARAMETERS.update({f'thickness={thickness}': (color_image, depth_image)})

        # One to each corner
        for n_obj in range(4):
            color_image, depth_image = np.copy(base_color), np.copy(base_depth)

            for location in [144, 288, 432, 576][:n_obj]:
                cv2.line(color_image, (location, 0), (location, 1280), (255, 0, 0), self.DEFAULT_THICKNESS)
                cv2.line(depth_image, (location, 0), (location, 1280), (255), self.DEFAULT_THICKNESS)

            self.PARAMETERS.update({f'n_obj={n_obj}': (color_image, depth_image)})

        # On default noise specturm
        for title, (color_image, depth_image) in common.noise().items():
            cv2.line(color_image, (360, 0), (360, 1280), (255, 0, 0), self.DEFAULT_THICKNESS)
            cv2.line(depth_image, (360, 0), (360, 1280), (255), self.DEFAULT_THICKNESS)

            self.PARAMETERS.update({f'{title} single': (color_image, depth_image)})

    def time_in_frame(self, color_image, depth_image):
        """
        Timing the pylon in frame detector.
        """
        detect_red(color_image, depth_image)
