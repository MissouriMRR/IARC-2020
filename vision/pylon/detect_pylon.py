"""
Determines whether the pylon is in the image or not, ignoring other objects
"""

import cv2
import numpy as np

# Set the lower and upper color limits
LOWER_RED = np.array([50, 150, 25])
UPPER_RED = np.array([255, 255, 120])

# Hold a treshold for the number of red pixels there should be in the image.
RED_THRESHOLD = 50


def detect_red(color_image, depth_image):
    """
    detect_red detects all pixels that fall in a certain range in an image
    then outputs the original image and detected mask

    Parameters
    ----------
    color_image: ndarray, three channel
        Image to detect pylon in.
    depth_image: ndarray, single channel
        Image to detect pylon in.

    Returns
    -------
    bool If pylon is in frame or not.
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
    red_pixels = 0
    for x in range(0, red_mask.shape[0]):
        for y in range(0, red_mask.shape[1]):
            if red_mask[x, y] != 0:
                red_pixels += 1

    # Return if the pylon was detected or not
    if red_pixels >= RED_THRESHOLD:
        return True
    else:
        return False


if __name__ == '__main__':
    image = cv2.imread("sim_pylon.png")
    print(detect_red(image, None))
