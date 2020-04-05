"""
module_orientation will calculate the orientation of the module in degrees
and return them as a tuple (x tilt, y tilt) using a derivative through the x- and y- axes
"""
import numpy as np
import argparse
from region_of_interest import region_of_interest


def get_module_orientation(roi, coordinates):
    """
    Finds the orientation of the module in degrees

    Parameters
    ----------
    roi: numpy array
        module region of interest calculated by region_of_interest
    coordinates: tuple of integers
        (x, y) coordinates of the center of the module in the frame
    """
    x_pos, y_pos = coordinates

    num_rows, num_cols = roi.shape
    print("rows: " + str(num_rows))
    print("cols: " + str(num_cols))

    x_diffs = 0
    for row in roi:
        x_diffs = x_diffs + (row[num_cols-1] / 1000 - row[0] / 1000)
        # x_diffs = x_diffs + np.mean(np.diff(row))

    x_avg_diff = x_diffs / num_rows

    x_tilt = np.degrees(np.arctan(x_avg_diff))

    np.transpose(roi)

    y_diffs = 0
    for col in roi:
        # "num_cols" being used again in the line below is not a mistake,
        #   it is still used in place of num_rows because of the transposition
        y_diffs = y_diffs + (col[num_cols - 1] / 1000 - col[0] / 1000)
        # y_diffs = y_diffs + np.mean(np.diff(col))

    y_avg_diff = y_diffs / num_cols

    y_tilt = np.degrees(np.arctan(y_avg_diff))

    return x_tilt, y_tilt


if __name__ == "__main__":
    """
    Driver main for module_orientation
    
    To test module_orientation, use
    "python module_orientation.py -i 
    
    Also note that region_of_interest should be in the same folder as module_orientation
    """
    # # Create object for parsing command-line options
    parser = argparse.ArgumentParser(description="Read .npy file and test for get_module_depth.\
                                            To read a .npy file, type \"python get_module_depth.py --i (image name).npy)\"")
    # # Add argument which takes path to a bag file as an input
    parser.add_argument("-i", "--input", type=str, help="Path to the .npy file")
    # # Parse the command line arguments to an object
    args = parser.parse_args()

    if args.input:
        depthNpy = args.input
    else:
        raise FileNotFoundError("No input parameter has been given. For help type --help")

    depthImage = np.load(depthNpy)

    # values for the test depth image
    center = (650, 560)
    roi = region_of_interest(depthImage, depthImage[560][650], center)

    get_module_orientation(roi, center)
