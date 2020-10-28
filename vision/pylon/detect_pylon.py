"""
Determines whether the pylon is in the image or not, ignoring other objects
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

# Set the lower and upper color limits
LOWER_RED = np.array([50, 150, 25])
UPPER_RED = np.array([255, 255, 120])

# Hold a treshold for the number of red pixels there should be in the image.
RED_THRESHOLD = 50


def detect_red(color_image, depth_image):
    """
    Counts the number of red(ish) pixels in an image.

    Parameters
    ----------
    color_image: ndarray, three channel
        Image to detect pylon in.
    depth_image: ndarray, single channel
        Image to detect pylon in.

    Returns
    -------
    list[BoundingBox] List with or without a pylon bounding box.
    """
    if color_image is None:
        raise ValueError("Image cannot be None.")

    # Convert the image from BGR to HSV
    hsv = cv2.cvtColor(color_image, cv2.COLOR_BGR2HSV)

    # Red_mask picks out any pixel between the lower and upper limits
    # and replaces them with white.  Everything else is replaced with black
    red_mask = cv2.inRange(hsv, LOWER_RED, UPPER_RED)
    # Run through each pixel in the mask. If over RED_THRESHOLD is white
    # then we have detected a pylon
    red_pixels = np.sum(red_mask) / 255

    # Return if the pylon was detected or not
    if red_pixels >= RED_THRESHOLD:
        return [
            BoundingBox(
                (0, 0, np.shape(color_image)[0], np.shape(color_image)[1]),
                ObjectType.PYLON,
            )
        ]
    else:
        return []


if __name__ == "__main__":
    image = cv2.imread("sim_pylon.png")
    print(detect_red(image, None))
