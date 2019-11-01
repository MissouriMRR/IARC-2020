import cv2
import numpy as np
from vision.blob.blob import Rectangle
import os
import json

def configure_params():
    params = cv2.SimpleBlobDetector_Params()

    with open('config.json', 'r') as config_file:
        config = json.load(config_file)

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