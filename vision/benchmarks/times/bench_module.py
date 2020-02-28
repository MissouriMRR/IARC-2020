"""
For testing all module algorithms.

Parameter Defaults
------------------
Resolution=(1280, 720)
Noise SD=0
N Objects = 0
"""
import os, sys
parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import cv2

import common

from vision.module.in_frame import ModuleInFrame


class TimeModuleInFrame:
    """
    Timing ModuleInFrame.
    """
    def setup(self):
        """
        Load images.
        """
        prefix = '' if os.path.isdir("times") else '..'

        ## Load images
        img_folder = os.path.join(prefix, '..', 'vision_images', 'module')

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

    def time_ModuleInFrame(self, color_image, depth_image):
        """
        Timing mif.
        """
        ModuleInFrame(color_image, depth_image)
