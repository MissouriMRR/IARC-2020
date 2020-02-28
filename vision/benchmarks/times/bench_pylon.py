"""
Runs through images and determines which have the pylon.

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
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import common

from vision.pylon.detect_pylon import detect_red


class TimePylon:
    """
    Timing all functionality of pylon project.
    """
    def setup(self):
        """
        Load images.
        """
        prefix = '' if os.path.isdir("times") else '..'

        ## Generate images
        img_folder = os.path.join(prefix, '..', 'vision_images', 'pylon')

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

    def time_in_frame(self, color_image, depth_image):
        """
        Timing the pylon in frame detector.
        """
        detect_red(color_image, depth_image)
