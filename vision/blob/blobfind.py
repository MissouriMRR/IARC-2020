import cv2
import numpy as np
import vision.blob.constants as constants
from vision.blob.blob import Rectangle
import os

def configure_params():
    params = cv2.SimpleBlobDetector_Params()

    params.filterByArea = True
    params.maxArea = constants.MAX_AREA

    params.minThreshold = constants.MIN_THRESHOLD
    params.maxThreshold = constants.MAX_THRESHOLD

    return params

def find_blobs(image, logging=False):
    """
    Detects blobs in a given image

    Parameters
    ----------
    image: string
        path to an image that can be interpreted by cv2.imread
    logging: bool
        whether to print a list of detected bounding boxes in the image

    Returns
    -------
    list[Rectangle]
        a list of bounding boxes represented as Rectangles, each with 8 (x, y, z) coordinates
    """
    image = cv2.imread(image)

    params = configure_params()
    blob_detector = cv2.SimpleBlobDetector_create(params)

    keypoints = blob_detector.detect(image)

    bounding_boxes = []
    for keypoint in keypoints:
        # find center and radius of keypoint
        x_coord, y_coord = keypoint.pt[0], keypoint.pt[1]
        radius = keypoint.size / 2

        # calculate coordinates for bounding box of each blob
        top_left_near = (x_coord - radius, y_coord - radius, 0)
        top_right_near = (x_coord + radius, y_coord - radius, 0)
        bottom_right_near = (x_coord + radius, y_coord + radius, 0)
        bottom_left_near = (x_coord - radius, y_coord + radius, 0)

        # With depth, these will be calculated differently
        top_left_far = top_left_near
        top_right_far = top_right_near
        bottom_right_far = bottom_right_near
        bottom_left_far = bottom_left_near

        # create Rectangle and add to list of bounding boxes
        bbox = Rectangle(top_left_near, top_right_near, bottom_right_near, bottom_left_near, top_left_far, top_right_far, bottom_right_far, bottom_left_far)
        bounding_boxes.append(bbox)


    if logging:
        im_with_keypoints = cv2.drawKeypoints(image, keypoints, outImage=np.array([]), color=(0, 225, 255), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
        print('Bounding boxes:', bounding_boxes)
        cv2.imshow("Blobs", im_with_keypoints)
        cv2.waitKey(0)

    return bounding_boxes


if __name__ == '__main__':
    for img in os.listdir('samples'):
        find_blobs('samples/' + os.fsdecode(img), True)