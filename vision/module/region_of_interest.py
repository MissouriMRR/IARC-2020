"""
Find region of interest for the orientation algorithm.
"""
import numpy as np
import argparse

# Constant
MODULE_HEIGHT = 76.2  # mm
MODULE_WIDTH = 50.8  # mm
VERTICAL_FOV = 57  # degrees?
HORIZONTAL_FOV = 86  # degrees
VERTICAL_RES = 1080  # p
HORIZONTAL_RES = 1920  # p

# ratio of the measured region_of_interest, use from 0 to 1
#   this should be used to ensure that the region_of_interest is trustworthy despite tilt
PADDING_CONSTANT = 0.85


def region_of_interest(depth_frame, depth_val, center):
    """
    Finds region of interest of the module in frame

    Parameters
    ----------
    depth_frame: ndarray
        The depth image.
    depth_val: float
        Measured value for the depth of the module from the camera.
    center: integer tuple
        Coordinates of the center of the module.

    Returns
    -------
    ndarray: A region of the depth image.
    """
    x_pos, y_pos = center

    # vertical angle of the module in the frame, from the center of the module to the top of the module
    vertical_region_angle = np.degrees(np.arctan((MODULE_HEIGHT / 2) / depth_val))

    # horizontal angle of the module in the frame, from the center of the module to its horizontal edge
    horizontal_region_angle = np.degrees(np.arctan((MODULE_WIDTH / 2) / depth_val))

    # both ratios should be only for one side, such that you can + or - some proportional value to the center to create region of interest
    vertical_angle_ratio = vertical_region_angle / (VERTICAL_FOV / 2)
    horizontal_angle_ratio = horizontal_region_angle / (HORIZONTAL_FOV / 2)

    vertical_image_portion = int(
        (vertical_angle_ratio * VERTICAL_RES / 2) * PADDING_CONSTANT
    )
    horizontal_image_portion = int(
        (horizontal_angle_ratio * HORIZONTAL_RES / 2) * PADDING_CONSTANT
    )

    return depth_frame[
        y_pos - vertical_image_portion : y_pos + vertical_image_portion,
        x_pos - horizontal_image_portion : x_pos + horizontal_image_portion,
    ]


if __name__ == "__main__":
    """
    Driver for testing region_of_interest
    """
    # # Create object for parsing command-line options
    parser = argparse.ArgumentParser(
        description='Read .npy file and test for get_module_depth.\
                                            To read a .npy file, type "python get_module_depth.py --i (image name).npy)"'
    )
    # # Add argument which takes path to a bag file as an input
    parser.add_argument("-i", "--input", type=str, help="Path to the .npy file")
    # # Parse the command line arguments to an object
    args = parser.parse_args()

    if args.input:
        depthImage = np.load(args.input)
    else:
        raise FileNotFoundError(
            "No input parameter has been given. For help type --help"
        )

    # gets rid of outliers, should be done before the arguments are calculated at all
    depthImage = np.clip(
        depthImage, np.percentile(depthImage, 10), np.percentile(depthImage, 90)
    )

    # test values, should be replaced with values found using other vision tools
    region_of_interest(depthImage, depthImage[560][650], (650, 560))
