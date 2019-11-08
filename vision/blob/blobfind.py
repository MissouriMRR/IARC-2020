"""
Detects blobs in images using OpenCV's SimpleBlobDetector.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import cv2
from vision.blob.blob import Rectangle
import json

def import_params():
    params = cv2.SimpleBlobDetector_Params()

    with open(os.path.join('vision', 'blob', 'config.json'), 'r') as config_file:
        config = json.load(config_file)
        config_file.close()

        for category in config:
            category_enabled = config[category]['enable']
            if category_enabled:
                if hasattr(params, category):
                    setattr(params, category, config[category]['enable'])
                for attr in config[category]:
                    if hasattr(params, attr):
                        setattr(params, attr, config[category][attr])

        print(params.minThreshold)
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
        if params is None:
            self.params = import_params()
        else:
            self.params = params

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