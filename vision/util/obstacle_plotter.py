"""
Utility for logging obstacles detected in an image
"""

import cv2
import numpy as np


def plot_obstacles(keypoints, image):
    """
    Shows the detected obstacles in an image and print the bounding boxes

    Parameters
    ----------
    keypoints: list[Keypoint]
        list of keypoint objects (obtainable from ObstacleFinder.keypoints)
        in the future, this should be changed to a list of Rectangle bounding boxes
    image: np.ndarray
        image to detect obstacles in
    """

    if not isinstance(keypoints, list):
        raise ValueError(f"Expected list of Keypoints, got {type(keypoints)} instead")
    if not isinstance(image, np.ndarray):
        raise ValueError(f"Expected argument of type ObstacleFinder, got {type(image)} instead")

    im_with_keypoints = cv2.drawKeypoints(image, keypoints, outImage=np.array([]), color=(255, 0, 255), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    # print formatted list of bounding boxes
    print('[')
    for bbox in keypoints:
        print('\tKeypoint:', bbox.pt[0], bbox.pt[1])
    print(']')

    # show image with circles indicating where obstacles were detected
    cv2.imshow("Obstacles", im_with_keypoints)
    cv2.waitKey(1)
