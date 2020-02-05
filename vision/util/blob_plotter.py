"""Utility for logging blobs detected in an image"""

import cv2
import numpy as np


def plot_blobs(keypoints, image):
    """
    Shows the detected blobs in an image and print the bounding boxes

    Parameters
    ----------
    keypoints: list[Keypoint]
        list of keypoint objects (obtainable from BlobFinder.keypoints)
        in the future, this should be changed to a list of Rectangle bounding boxes
    image: np.ndarray
        image to detect blobs in
    """

    if not isinstance(keypoints, list):
        raise ValueError(f"Expected list of Keypoints, got {type(keypoints)} instead")
    if not isinstance(image, np.ndarray):
        raise ValueError(f"Expected argument of type BlobFinder, got {type(image)} instead")

    im_with_keypoints = cv2.drawKeypoints(image, keypoints, outImage=np.array([]), color=(255, 0, 255), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    # print formatted list of bouding boxes
    print('[')
    for bbox in keypoints:
        print('\tKeypoint:', bbox.pt[0], bbox.pt[1])
    print(']')

    # show image with circles indicating where blobs were detected
    cv2.imshow("Blobs", im_with_keypoints)
    cv2.waitKey(1)
