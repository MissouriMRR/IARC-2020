"""
region_of_interest will
given the depth value (float) in millimeters

The __main__ of this file acts as a driver for testing region_of_interest
"""
import numpy as np
import argparse
import matplotlib.pyplot as plt

# Constant
MODULE_HEIGHT = 76.2  # mm
MODULE_WIDTH = 50.8  # mm
VERTICAL_FOV = 57  # degrees?
HORIZONTAL_FOV = 86  # degrees
VERTICAL_RES = 1080  # p
HORIZONTAL_RES = 1920  # p

# ratio of the measured region_of_interest, use from 0 to 1
#   this should be used to ensure that the region_of_interest is trustworthy despite tilt
PADDING_CONSTANT = .85

# TODO: account for general orientation (horizontal or vertical) and switch horizontal/vertical accordingly
# keep in mind that, as of right now, the method assumes that the module is vertically oriented, and the best
#   solution to account for it is to decrease the PADDING_CONSTANT
# TODO: remove testing components, such as passing depth_frame to method and modifying data for visualization


def region_of_interest(depth_val, depth_frame):
    """
    Finds region of interest of the module in frame

    Parameters
    ----------
    depth_val: float
        Measured value for the depth of the module from the camera
    """
    # vertical angle of the module in the frame, from the center of the module to the top of the module
    vertical_region_angle = np.degrees(np.arctan((MODULE_HEIGHT / 2) / depth_val))

    # horizontal angle of the module in the frame, from the center of the module to its horizontal edge
    horizontal_region_angle = np.degrees(np.arctan((MODULE_WIDTH / 2) / depth_val))

    # both ratios should be only for one side, such that you can + or - some proportional value to the center to create region of interest
    vertical_angle_ratio = vertical_region_angle / (VERTICAL_FOV / 2)
    horizontal_angle_ratio = horizontal_region_angle / (HORIZONTAL_FOV / 2)

    vertical_image_portion = int((vertical_angle_ratio * VERTICAL_RES / 2) * PADDING_CONSTANT)
    horizontal_image_portion = int((horizontal_angle_ratio * HORIZONTAL_RES / 2) * PADDING_CONSTANT)

    depth_frame[650 - vertical_image_portion:650 + vertical_image_portion, 560 - horizontal_image_portion:560 + horizontal_image_portion] = 0

    plt.imshow(depth_frame)
    plt.show()


if __name__ == "__main__":
    """
    
    """
    # # Create object for parsing command-line options
    parser = argparse.ArgumentParser(description="Read .npy file and test for get_module_depth.\
                                            To read a .npy file, type \"python get_module_depth.py --i (image name).npy)\"")
    # # Add argument which takes path to a bag file as an input
    parser.add_argument("-i", "--input", type=str, help="Path to the .npy file")
    # # Parse the command line arguments to an object
    args = parser.parse_args()

    # if args.input:
    #     depthNpy = args.input
    # else:
    #     raise FileNotFoundError("No input parameter has been given. For help type --help")

    depthImage = np.load(args.input)

    region_of_interest(depthImage[560][650], depthImage)


