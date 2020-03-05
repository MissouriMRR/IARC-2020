"""
For testing all module algorithms.

Parameter Defaults
------------------
Resolution = (1280, 720)
Noise SD = 0
N Objects = 0
"""
import os, sys
parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
gggparent_dir = os.path.dirname(ggparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir, gggparent_dir]

import numpy as np
import cv2

import common

from vision.module.in_frame import ModuleInFrame


class TimeModuleInFrame:
    """
    Timing ModuleInFrame.
    """
    DEFAULT_DIMS = (1280, 720)
    DEFAULT_RADIUS = 50

    def setup(self):
        """
        Load images.
        """
        ## Generate images
        self.PARAMETERS = {}

        self.PARAMETERS.update(common.blank_dimensions())

        base_color, base_depth = common.blank_dimensions(self.DEFAULT_DIMS)

        # Size of rectangle and radius of circle
        for size in [20, 40, 80, 100, 120]:
            color_image, depth_image = np.copy(base_color), np.copy(base_depth)

            cv2.rectangle(color_image, (213, 240), (426+size, 480+size), (255, 255, 255), thickness=4)
            cv2.rectangle(depth_image, (213, 240), (426+size, 480+size), (255), thickness=4)

            for location in [(640+213, 240), (640+213, 480), (640+426, 240), (640+426, 480)]:
                cv2.circle(color_image, location, size, (255, 255, 255), thickness=4)
                cv2.circle(depth_image, location, size, (255), thickness=4)

            self.PARAMETERS.update({f'size={size}': (color_image, depth_image)})

        # Adding more circles
        for n_obj in range(4, 9):
            color_image, depth_image = np.copy(base_color), np.copy(base_depth)

            cv2.rectangle(color_image, (213, 240), (426, 480), (255, 255, 255), thickness=4)
            cv2.rectangle(depth_image, (213, 240), (426, 480), (255), thickness=4)

            for location in [
                    (800, 180), (800, 360), (800, 540), (960, 180), (960, 360),
                    (960, 540), (1120, 180), (1120, 360), (1120, 540)][:n_obj]:
                cv2.circle(color_image, location, self.DEFAULT_RADIUS, (255, 255, 255), thickness=4)
                cv2.circle(depth_image, location, self.DEFAULT_RADIUS, (255), thickness=4)

            self.PARAMETERS.update({f'n_circle={n_obj}': (color_image, depth_image)})

        # On default noise specturm
        for title, (color_image, depth_image) in common.noise().items():
            cv2.rectangle(color_image, (213, 240), (426, 480), (255, 255, 255), thickness=4)
            cv2.rectangle(depth_image, (213, 240), (426, 480), (255), thickness=4)

            for location in [(640+213, 240), (640+213, 480), (640+426, 240), (640+426, 480)]:
                cv2.circle(color_image, location, self.DEFAULT_RADIUS, (255, 255, 255), thickness=4)
                cv2.circle(depth_image, location, self.DEFAULT_RADIUS, (255), thickness=4)

            self.PARAMETERS.update({f'{title} single': (color_image, depth_image)})

    def time_ModuleInFrame(self, color_image, depth_image):
        """
        Timing mif.
        """
        ModuleInFrame(color_image, depth_image)
