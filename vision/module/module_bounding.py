"""
Find the region of the image that the module lies within.
"""

import numpy as np

MODULE_HEIGHT = 76.2  # mm
MODULE_WIDTH = 50.8  # mm
VERTICAL_FOV = 57  # degrees
HORIZONTAL_FOV = 86  # degrees

PADDING_CONSTANT = 1.15

def getModuleBounds(dimensions, center, depth):
    """
    getModuleBounds will find four coordinates within the module that will be used to create a BoundingBox.

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
    vert_res, horiz_res, _ = dimensions

    vert_angle = np.degrees(np.arctan((MODULE_HEIGHT / 2) / depth))
    horiz_angle = np.degrees(np.arctan((MODULE_HEIGHT / 2) / depth))

    vert_ratio = vert_angle / (VERTICAL_FOV / 2)
    horiz_ratio = horiz_angle / (HORIZONTAL_FOV / 2)

    vert_val = int((vert_ratio * vert_res / 2) * PADDING_CONSTANT)
    horiz_val = int((horiz_ratio * horiz_res / 2) * PADDING_CONSTANT)

    top_left = (x - horiz_val, y - vert_val)
    top_right = (x + horiz_val, y - vert_val)
    bottom_right = (x + horiz_val, y + vert_val)
    bottom_left = (x - horiz_val, y + vert_val)

    return [top_left, top_right, bottom_right, bottom_left]