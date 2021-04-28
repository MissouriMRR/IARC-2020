"""
get_module_depth will return a float value for the relative depth of the module in the camera frame in millimeters.
"""
import numpy as np

# Constants
SEARCH_RADIUS = 20

def get_module_depth(depth_image: np.ndarray, coordinates: tuple) -> float:
    """
    Finds relative depth of the module.

    Parameters
    ----------
    depth_image: ndarray
        The depth image.
    coordinates: tuple<int>
        (x, y) coordinates of the center of the module in the frame.

    Returns
    -------
    float: Depth of the module (in millimeters).
    """
    x_pos, y_pos = coordinates # coordinates of center of module

    direct_center_depth = depth_image[y_pos][x_pos] # depth at the center

    adjusted_radius = SEARCH_RADIUS

    # Adjust search radius based on center depth
    if direct_center_depth != 0:

        # 750 chosen as a rough median for depth values
        search_radius_multipler = direct_center_depth / 750

        # inverted because higher depth values means further away
        if search_radius_multipler > 2:
            search_radius_multipler = 0.01
        elif search_radius_multipler > 1:
            search_radius_multipler = 1 - (search_radius_multipler - 1)
        else:
            search_radius_multipler = 1 + (1 - search_radius_multipler)

        adjusted_radius = int(round(SEARCH_RADIUS * search_radius_multipler))

        if adjusted_radius < 10:
            adjusted_radius = 10

    depth_values_in_radius = depth_image[
        y_pos - adjusted_radius : y_pos + adjusted_radius,
        x_pos - adjusted_radius : x_pos + adjusted_radius,
    ]

    # Gets rid of 0 depth values
    depth_values_in_radius = depth_values_in_radius[depth_values_in_radius != 0]

    avg = np.mean(depth_values_in_radius)
    if np.isnan(avg):
        return 0
    return avg


if __name__ == "__main__":
    """
    To test get_module_depth, use
    "python get_module_depth.py -i (image name).npy"

    Also note that in_frame, must be in the same file location,
    or a path must be specified
    """
    import argparse

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

    # Hard code the x and y coordinates for testing purposes
    print("Depth of module: " + str(get_module_depth(depthImage, (886, 823))))
    print("Depth at center parameter: " + str(depthImage[886][823]))
