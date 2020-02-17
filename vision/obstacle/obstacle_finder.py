"""
Detects obstacles in images using OpenCV's SimpleBlobDetector
"""
import os
import sys

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import cv2
import numpy as np
from vision.bounding_box import BoundingBox, ObjectType
import json
from vision.util.import_params import import_params


class ObstacleFinder:
    """
    Constructs an ObstacleFinder object with an image, logging, and params

    Parameters
    ----------
    params: SimpleBlobDetector_Params
        SimpleBlobDetector params object
    """
    def __init__(self, params=None):
        self.keypoints = []
        self.params = params
        self.blob_detector = cv2.SimpleBlobDetector_create(self.params)

    @property
    def params(self):
        """
        This function is called every time self.params is run.
        """
        return self._params

    @params.setter
    def params(self, value):
        """
        Defines behavior of self.params = value.
        """
        if not isinstance(value, cv2.SimpleBlobDetector_Params):
            raise ValueError(f"Requires instance of SimpleBlobDetector_Params, got {type(value)}")

        self._params = value
        self.blob_detector = cv2.SimpleBlobDetector_create(self.params)

    def find(self, image):
        """
        Detects obstacles in the image provided in the constructor

        Parameters
        ----------
        image: np.ndarray
            image to find obstacles in

        Returns
        -------
        list[BoundingBox]
            a list of bounding boxes represented as Rectangles, each with 8 (x, y, z) coordinates
        """

        if not isinstance(image, np.ndarray):
            raise ValueError(f"Requires image as np.ndarray, got {type(image)}")

        keypoints = self.blob_detector.detect(image)
        self.keypoints = keypoints

        bounding_boxes = []
        for keypoint in keypoints:
            # find center and radius of keypoint
            center_x, center_y = keypoint.pt[0], keypoint.pt[1]
            radius = keypoint.size / 2

            # calculate coordinates for bounding box of each obstacle
            pos_dx = center_x + radius
            neg_dx = center_x - radius
            pos_dy = center_y + radius
            neg_dy = center_y - radius

            top_left_near = (neg_dx, neg_dy, 0)
            top_right_near = (pos_dx, neg_dy, 0)
            bottom_right_near = (pos_dx, pos_dy, 0)
            bottom_left_near = (neg_dx, pos_dy, 0)

            # With depth, these will be calculated differently
            top_left_far = top_left_near
            top_right_far = top_right_near
            bottom_right_far = bottom_right_near
            bottom_left_far = bottom_left_near

            vertices = [top_left_near, top_right_near, bottom_right_near, bottom_left_near, top_left_far, top_right_far, bottom_right_far, bottom_left_far]

            # create Rectangle and add to list of bounding boxes
            bbox = BoundingBox(vertices, ObjectType.AVOID)
            bounding_boxes.append(bbox)

        return bounding_boxes


if __name__ == '__main__':
    from vision.util.box_plotter import plot_box

    prefix = 'vision' if os.path.isdir("vision") else ''
    img_folder = os.path.join(prefix, 'vision_images', 'obstacle')
    config_filename = os.path.join(prefix, 'obstacle', 'config.json')

    with open(config_filename, 'r') as config_file:
        config = json.load(config_file)

    for img in os.listdir(img_folder):
        if img[-4:] not in ['.png', '.jpg']:
            continue

        image = cv2.imread(os.path.join(img_folder, os.fsdecode(img)))

        obstacle_finder = ObstacleFinder(params=import_params(config))
        bboxes = obstacle_finder.find(image)

        plot_box(bboxes, image)
