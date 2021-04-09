"""
Find the region of the image that the module lies within.
"""

import numpy as np
import cv2
import argparse

MODULE_HEIGHT = 76.2  # mm
MODULE_WIDTH = 50.8  # mm
VERTICAL_FOV = 57  # degrees
HORIZONTAL_FOV = 86  # degrees

PADDING_CONSTANT = 1.15


def get_module_bounds(dimensions, center, depth):
    """
    get_module_bounds will find four coordinates within the module that will be used to create a BoundingBox.

    Parameters
    ----------
    dimensions: tuple<int>
        The dimensions of the color image.
    center: tuple<int>
        (x, y)-coordinates of the center of the module
    depth: float
        Value of the depth of the center of the module from the camera.

    Returns
    -------
    list - list of the four tuple vertices.
    """
    x, y = center
    vert_res, horiz_res, channels = np.shape(dimensions)

    vert_angle = np.degrees(np.arctan((MODULE_HEIGHT / 2) / depth))
    horiz_angle = np.degrees(np.arctan((MODULE_WIDTH / 2) / depth))

    vert_ratio = vert_angle / (VERTICAL_FOV / 2)
    horiz_ratio = horiz_angle / (HORIZONTAL_FOV / 2)

    vert_val = int((vert_ratio * vert_res / 2) * PADDING_CONSTANT)
    horiz_val = int((horiz_ratio * horiz_res / 2) * PADDING_CONSTANT)

    top_left = (x - horiz_val, y - vert_val)
    top_right = (x + horiz_val, y - vert_val)
    bottom_right = (x + horiz_val, y + vert_val)
    bottom_left = (x - horiz_val, y + vert_val)

    return [top_left, top_right, bottom_right, bottom_left]


if __name__ == "__main__":
    """
    Driver for testing module_bounding
    """
    # # Create object for parsing command-line options
    parser = argparse.ArgumentParser(
        description='Read .npy file and test for get_module_depth.\
                                            To read a .npy file, type "python module_bounding.py --i (image number))"'
    )
    # # Add argument which takes path to a bag file as an input
    parser.add_argument("-i", "--input", type=str, help="Path to the .npy file")
    # # Parse the command line arguments to an object
    args = parser.parse_args()

    if args.input:
        colorImage = cv2.imread(args.input + "-colorImage.jpg")
        depthImage = np.load(args.input + "-depthImage.npy")
    else:
        raise FileNotFoundError(
            "No input parameter has been given. For help type --help"
        )

    # gets rid of outliers, should be done before the arguments are calculated at all
    depthImage = np.clip(
        depthImage, np.percentile(depthImage, 10), np.percentile(depthImage, 90)
    )

    tl, tr, br, bl = get_module_bounds((1080, 1920), (995, 600), depthImage[600][995])
    colorImage = colorImage[tl[1] : bl[1], bl[0] : br[0]]

    cv2.imshow("Module Bounding", colorImage)
    cv2.waitKey(0)
