"""
Detects blobs in images using OpenCV's SimpleBlobDetector.
"""
import os
import sys

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import cv2
import numpy as np
from vision.interface import Rectangle
import json


def import_params(config):
    if type(config) is not dict:
        raise ValueError(f"When importing params, config should be a dictionary, got {type(config)} instead")

    params = cv2.SimpleBlobDetector_Params()

    for category in config:
        if 'enable' not in config[category]:
            raise ValueError(f"Category '{category}' is missing an 'enable' attribute")
        category_enabled = config[category]['enable']
        if category_enabled:
            if hasattr(params, category):
                setattr(params, category, config[category]['enable'])
            for attr in config[category]:
                if hasattr(params, attr):
                    setattr(params, attr, config[category][attr])

    return params


class BlobFinder:
    """
    Constructs a BlobFinder object with an image, logging, and params

    Parameters
    ----------
    image: np array
        image to detect blobs in, as a np array
    params: SimpleBlobDetector_Params
        blob detector params object
    """
    def __init__(self, image, params=None):
        self.image = image
        self.keypoints = []
        self.params = params
        self.blob_detector = cv2.SimpleBlobDetector_create(self.params)

    @property
    def image(self):
        """
        This function is called every time self.image is run.
        """
        return self._image

    @image.setter
    def image(self, value):
        """
        Defines behavior of self.image = value.
        """
        if not isinstance(value, np.ndarray):
            raise ValueError("Requires image as np.ndarray")

        self._image = value

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
            raise ValueError("Requires instance of SimpleBlobDetector_Params")

        self._params = value
        self.blob_detector = cv2.SimpleBlobDetector_create(self.params)

    def find(self):
        """
        Detects blobs in the image provided in the constructor

        Returns
        -------
        list[Rectangle]
            a list of bounding boxes represented as Rectangles, each with 8 (x, y, z) coordinates
        """

        keypoints = self.blob_detector.detect(self.image)
        self.keypoints = keypoints

        bounding_boxes = []
        for keypoint in keypoints:
            # find center and radius of keypoint
            center_x, center_y = keypoint.pt[0], keypoint.pt[1]
            radius = keypoint.size / 2

            # calculate coordinates for bounding box of each blob
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
            bbox = Rectangle(vertices, None)
            bounding_boxes.append(bbox)

        return bounding_boxes


if __name__ == '__main__':
    from vision.util.blob_plotter import plot_blobs

    prefix = 'vision' if os.path.isdir("vision") else ''
    img_folder = os.path.join(prefix, 'vision_images', 'blob')
    config_filename = os.path.join(prefix, 'blob', 'config.json')

    with open(config_filename, 'r') as config_file:
        config = json.load(config_file)

    for img in os.listdir(img_folder):
        if img[-4:] not in ['.png', '.jpg']:
            continue

        image = cv2.imread(os.path.join(img_folder, os.fsdecode(img)))

        blob_finder = BlobFinder(image, params=import_params(config))
        bboxes = blob_finder.find()

        plot_blobs(blob_finder.keypoints, image)
