"""Utility for logging blobs detected in an image"""

import cv2
import numpy as np
try:
    from vision.blob.blobfind import BlobFinder
except ImportError:
    from blob.blobfind import BlobFinder

def log_blobs(blob_finder):
    """
    Shows the detected blobs in an image and print the bounding boxes

    Parameters
    ----------
    blob_finder: BlobFinder
        BlobFinder object that contains an image and potentially params
    """

    if not isinstance(blob_finder, BlobFinder):
        exit(f"Expected argument of type BlobFinder, got {type(blob_finder)} instead")

    image = blob_finder.image
    bounding_boxes = blob_finder.find()
    keypoints = blob_finder.keypoints
    im_with_keypoints = cv2.drawKeypoints(image, keypoints, outImage=np.array([]), color=(255, 0, 0), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    # print formatted list of bouding boxes
    print('[')
    for bbox in bounding_boxes:
        print('\t', bbox)
    print(']')

    # show image with circles indicating where blobs were detected
    cv2.imshow("Blobs", im_with_keypoints)
    cv2.waitKey(0)
