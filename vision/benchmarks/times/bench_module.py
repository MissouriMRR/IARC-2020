"""
For testing all module algorithms.
"""
import os, sys
parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import cv2

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

        self.images = []
        for filename in os.listdir(img_folder):
            if filename[-4:] not in ['.png', '.jpg']:
                continue

            img_path = os.path.join(img_folder, os.fsdecode(filename))

            image = cv2.imread(img_path)

            self.images.append((image, None))

    def time_ModuleInFrame(self):
        """
        Timing mif.
        """
        for color_image, depth_image in self.images:
            ModuleInFrame(color_image, depth_image)
