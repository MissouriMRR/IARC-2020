"""
Obstacle detector unit tests.
"""
import os, sys

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import json

from vision.obstacle.obstacle_finder import ObstacleFinder
from vision.util.import_params import import_params


IMG_FOLDER = 'obstacle'

class AccuracyObstacle:
    """
    Measuring accuracy of obstacle detection.
    """
    def setup(self):
        """
        Setup obstacle detector
        """
        prefix = '' if os.path.isdir("times") else '..'

        config_filename = os.path.join(prefix, '..', 'obstacle', 'config.json')

        with open(config_filename, 'r') as config_file:
            config = json.load(config_file)

        self.blob_finder = ObstacleFinder(params=import_params(config))

    def accuracy_find(self, color_image, depth_image):
        """
        Test accuracy of obstacle finder via custom Annotations w/ blob_annotator tool.

        Returns
        -------
        List[BoundingBox]
        """
        bounding_boxes = self.obstacle_finder.find(color_image, depth_image)

        return bounding_boxes
