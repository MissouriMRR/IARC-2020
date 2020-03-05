"""
For testing all module algorithms.
"""
import os, sys
parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
gggparent_dir = os.path.dirname(ggparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir, gggparent_dir]

from vision.module.in_frame import ModuleInFrame as mif


IMG_FOLDER = 'module'

class AccuracyModuleInFrame:
    """
    Testing module.in_frame accuracy.
    """
    def accuracy_ModuleInFrame(self, color_image, depth_image):
        """
        Measuring accuracy of ModuleInFrame

        Returns
        -------
        List[BoundingBox]
        """
        bounding_boxes = mif(color_image, depth_image)

        return bounding_boxes
