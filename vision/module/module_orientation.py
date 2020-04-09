"""
module_orientation will calculate the orientation of the module in degrees
and return them as a tuple (x tilt, y tilt) using a derivative through the x- and y- axes
"""
import numpy as np


def get_module_orientation(roi):
    """
    Finds the orientation of the module in degrees

    Parameters
    ----------
    roi: numpy array
        module region of interest calculated by region_of_interest

    Returns
    -----------
    tuple of floating point values, degrees in coordinates of
        the tilt on the x and y axes, respectively
    """
    x_avg_diff = np.mean(roi[:, -1] / 1000 - roi[:, 0] / 1000)
    x_tilt = np.degrees(np.arctan(x_avg_diff))


    y_avg_diff = np.mean(roi.T[:, -1] / 1000 - roi.T[:, 0] / 1000)
    y_tilt = np.degrees(np.arctan(y_avg_diff))

    return x_tilt, y_tilt


if __name__ == "__main__":
    """
    Driver main for module_orientation
    
    To test module_orientation, use
    "python module_orientation.py -i {depthimage.npy}"
    
    Also note that region_of_interest should be in the same folder as module_orientation
    """
    import argparse
    from region_of_interest import region_of_interest

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

    get_module_orientation(roi)
