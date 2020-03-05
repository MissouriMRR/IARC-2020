"""
Runs through images and determines which have the pylon
"""
import os, sys
parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
gggparent_dir = os.path.dirname(ggparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir, gggparent_dir]

from vision.pylon.detect_pylon import detect_red


IMG_FOLDER = 'pylon'

class AccuracyPylon:
    """
    Accuracy of pylon detector.
    """
    def accuracy_pylon(self, color_image, depth_image):
        """
        Measuring accuracy of detect red.

        Returns
        -------
        List[BoundingBox]
        """
        bounding_boxes = detect_red(color_image, depth_image)

        return bounding_boxes
