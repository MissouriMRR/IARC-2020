"""
Detects blobs in images using OpenCV's SimpleBlobDetector.
"""

import cv2
import numpy as np
from vision.blob.blob import Rectangle
import os
import json


def import_params():
    params = cv2.SimpleBlobDetector_Params()

    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
        config_file.close()

        for category in config:
            for attr in category:
                setattr(params, attr, config[category][attr])

        threshold_config = config['threshold']
        if threshold_config['filter_by_threshold']:
            params.minThreshold = threshold_config['min_threshold']
            params.maxThreshold = threshold_config['max_threshold']
            params.thresholdStep = threshold_config['threshold_step']

        area_config = config['area']
        params.filterByArea = area_config['filter_by_area']
        params.minArea = area_config['min_area']
        params.maxArea = area_config['max_area']

        color_config = config['color']
        params.filterByColor = color_config['filter_by_color']
        params.blobColor = color_config['blob_color']

        convexity_config = config['convexity']
        params.filterByConvexity = convexity_config['filter_by_convexity']
        params.minConvexity = convexity_config['min_convexity']
        params.maxConvexity = convexity_config['max_convexity']

        inertia_config = config['inertia_ratio']
        params.filterByInertia = inertia_config['filter_by_inertia']
        params.minInertiaRatio = inertia_config['min_inertia_ratio']
        params.maxInertiaRatio = inertia_config['max_inertia_ratio']

        occurrences_config = config['occurrences']
        if occurrences_config['filter_by_occurrences']:
            params.minDistBetweenBlobs = occurrences_config['min_dist_between_blobs']
            params.minRepeatability = occurrences_config['min_repeatability']

    return params


class BlobFinder:
    """
    Constructs a BlobFinder object with an image, logging, and params

    Parameters
    ----------
    image: np array
        image to detect blobs in, as a np array
    config: kwargs
        configuration options, such as blob detector params
    """
    def __init__(self, image, **config):
        self.image = image
        if 'params' in config:
            self.params = config['params']
        else:
            self.params = import_params()

    def update_image(self, image):
        self.image = image

    def update_params(self, params):
        self.params = params

    """
    Detects blobs in the image provided in the constructor

    Returns
    -------
    list[Rectangle]
        a list of bounding boxes represented as Rectangles, each with 8 (x, y, z) coordinates
    """
    def find(self):
        blob_detector = cv2.SimpleBlobDetector_create(self.params)
        keypoints = blob_detector.detect(self.image)

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

            # create Rectangle and add to list of bounding boxes
            bbox = Rectangle(top_left_near, top_right_near, bottom_right_near, bottom_left_near, top_left_far,
                             top_right_far, bottom_right_far, bottom_left_far)
            bounding_boxes.append(bbox)

        return bounding_boxes


if __name__ == '__main__':
    for img in os.listdir('samples'):
        image = cv2.imread('samples/' + os.fsdecode(img))
        blob_finder = BlobFinder(image, params=import_params())
        bboxes = blob_finder.find()