"""
Text related unit tests.

Parameter Defaults
------------------
Resolution = (1280, 720)
Noise SD = 0
N Objects = 1
N Letters = 5
Colors = White text on black bg
Size = 3
"""
import os, sys
parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import numpy as np
import cv2

import common

from boat.detect_words import TextDetector


class TimeDetectRussianWord:
    """
    Testing the text detector.
    """
    DEFAULT_WORD = 'holye'  # pronounced hol.ee
    DEFAULT_DIMS = (1280, 720)
    DEFAULT_SIZE = 3

    def setup(self):
        """
        Load images.
        """
        ## Generate images
        self.PARAMETERS = {}

        self.PARAMETERS.update(common.blank_dimensions())

        base_color, base_depth = common.blank_dimensions(self.DEFAULT_DIMS)

        # Small text to 1/4 image
        for size in [1, 3, 6, 10]:
            color_image, depth_image = np.copy(base_color), np.copy(base_depth)

            cv2.putText(color_image, self.DEFAULT_WORD, (640, 360), cv2.FONT_HERSHEY_SIMPLEX,
                        size, (255, 255, 255), 3)
            cv2.putText(depth_image, self.DEFAULT_WORD, (640, 360), cv2.FONT_HERSHEY_SIMPLEX,
                        size, (255), 3)

            self.PARAMETERS.update({f'size={size}': (color_image, depth_image)})

        # One to each corner
        for n_text in range(4):
            color_image, depth_image = np.copy(base_color), np.copy(base_depth)

            for location in [(320, 180), (320, 540), (960, 180), (960, 540)][:n_text]:
                cv2.putText(color_image, self.DEFAULT_WORD, location, cv2.FONT_HERSHEY_SIMPLEX,
                            self.DEFAULT_SIZE, (255, 255, 255), 3)
                cv2.putText(depth_image, self.DEFAULT_WORD, location, cv2.FONT_HERSHEY_SIMPLEX,
                            self.DEFAULT_SIZE, (255), 3)

            self.PARAMETERS.update({f'n_text={n_text}': (color_image, depth_image)})

        # On default noise specturm
        for title, (color_image, depth_image) in common.noise().items():
            cv2.putText(color_image, self.DEFAULT_WORD, (640, 360), cv2.FONT_HERSHEY_SIMPLEX,
                        self.DEFAULT_SIZE, (255, 255, 255), 3)
            cv2.putText(depth_image, self.DEFAULT_WORD, (640, 360), cv2.FONT_HERSHEY_SIMPLEX,
                        self.DEFAULT_SIZE, (255), 3)

            self.PARAMETERS.update({f'{title} single': (color_image, depth_image)})

    def time_detector(self, color_image, depth_image):
        """
        Timing detectRussianWord.
        """
        TextDetector().detect_russian_word(color_image, depth_image)
