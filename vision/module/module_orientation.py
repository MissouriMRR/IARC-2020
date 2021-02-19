"""
get_module_orientation will calculate the orientation of the module in degrees
and return them as a tuple (x tilt, y tilt) using a derivative through the x- and y- axes

get_module_roll will calculate the roll of the module in degrees with respect to the y axis
"""
import numpy as np
import cv2


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


def get_module_roll(enclosing_region: np.ndarray) -> float:
    """
    Finds the roll of the module in degrees

    Parameters
    ----------
    enclosing_region: numpy array
        region of the image with the module, calculated by module_bounding
        image is supposed to be padded enough to include the entire

    Returns
    -----------
    roll
        module roll with respect to the positive y axis in degrees
    """
    # contours only work on grey images
    enclosing_region = cv2.cvtColor(enclosing_region, cv2.COLOR_BGR2GRAY)

    edges = cv2.Canny(enclosing_region, 150, 450)

    contours = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[0]
    # use the following line to visualize contours, pair with imshow
    # colorImage = cv2.drawContours(enclosing_region, contours, -1, (0, 255, 0), 3)

    # simple contours will contain the list of contours with fewer than 8 vertices
    simple_contours = []
    for c in contours:
        approx = cv2.approxPolyDP(c, 0.01 * cv2.arcLength(c, True), True)
        if len(approx) < 8:
            simple_contours.append(c)

            # more visualization stuff
            # enclosing_region = cv2.drawContours(enclosing_region, c, -1, (0, 255, 0), 3)

    # draws minimum area rectangles to enclose the contours
    # presumably, since thee module contours (or module edge contours) will rectangles at some angle,
    #   the min area rectangles will be at or around that same angle
    rectangles = [cv2.minAreaRect(c) for c in simple_contours]

    # for visualization, if desired
    # enclosing_region = cv2.cvtColor(enclosing_region, cv2.COLOR_GRAY2BGR)

    # to visualize min area rectangles
    # for rect in rectangles:
    #     box = cv2.boxPoints(rect)
    #     box = np.int0(box)
    #     cv2.drawContours(colorImage, [box], 0, (0, 0, 255), 2)

    np_rectangles = np.asarray(rectangles)
    angles = np_rectangles[:, 2]

    # if the angle is absurd, it won't be taken
    #   if the module is truly rolled at over 45 degrees, minAreaRect
    #   should simply choose a different rectangle or axis
    mask = np.where(abs(angles) < 45)
    roll = np.mean(angles[mask])

    return roll


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
    parser = argparse.ArgumentParser(
        description='Read .npy file and test for get_module_depth.\
                                            To read a .npy file, type "python get_module_depth.py --i (image name).npy)"'
    )
    # # Add argument which takes path to a bag file as an input
    parser.add_argument("-i", "--input", type=str, help="Path to the .npy file")
    # # Parse the command line arguments to an object
    args = parser.parse_args()

    if args.input:
        depthNpy = args.input
    else:
        raise FileNotFoundError(
            "No input parameter has been given. For help type --help"
        )

    depthImage = np.load(depthNpy)

    # to test roll, import getModuleBounds from module_bounding and use that to find the enclosing region

    # values for the test depth image
    center = (650, 560)
    roi = region_of_interest(depthImage, depthImage[560][650], center)

    get_module_orientation(roi)
