"""
This file contains the ModuleInFrame function to detect if the module is in an image
"""
import cv2
import numpy as np

# Constants
BLUR_SIZE = 5 # Blur kernel size
BUCKET_MODIFIER = 1 # Changes how many buckets are in the range
MIN_SLOPES_IN_BUCKET = 15 # Minimum number of slopes in a single bucket to identify the module


def ModuleInFrame(img):
    """
    Determines if the Module is in frame

    Parameters
    ----------
    img: numpy array
        The image stored in a numpy array.

    Returns
    -------
    bool: true if the module is in the frame and false if not in the frame
    """
    if img is None:
        raise ValueError(f"Image cannot be None.")

    # Ignore numpy warnings
    np.seterr(all="ignore")

    # Remove depth channel
    img = img[:, :, :3]

    # Grayscale
    gray = cv2.cvtColor(src=img, code=cv2.COLOR_RGB2GRAY)

    # Guassian Blur
    blur = cv2.GaussianBlur(src=gray, ksize=(BLUR_SIZE, BLUR_SIZE), sigmaX=0)

    # Laplacian Transform
    laplacian = cv2.Laplacian(src=blur, ddepth=cv2.CV_8U, ksize=3)
    laplacian = np.uint8(laplacian)

    # Hough Circle Detection
    # circles = (x, y, r)
    circles = cv2.HoughCircles(image=laplacian, method=cv2.HOUGH_GRADIENT, dp=1, minDist=8, param1=50, param2=40, minRadius=0, maxRadius=50)

    if circles is None:
        return False

    circles = np.uint16(circles)

    # Resize circles into 2d array
    circles = np.reshape(circles, (np.shape(circles)[1], 3))

    # Finding slopes between the circles
    slopes = np.array([])
    for x, y, _ in circles:
        for iX, iY, __ in circles:
            m = (iY - y) / (iX - x)
            # slope must be non-infinite and can't be between the same circle
            if (not np.isnan(m)) and (not np.isinf(m)) and (x != iX and y != iY):
                slopes = np.append(slopes, m)

    # Converting slopes to degrees
    slopes = np.degrees(np.arctan(slopes))

    # Bucket sorting slopes to group parallels
    upper_bound = np.amax(slopes)
    lower_bound = np.amin(slopes)
    num_buckets = np.int32(upper_bound - lower_bound) * BUCKET_MODIFIER

    buckets, _ = np.histogram(slopes, num_buckets, (lower_bound, upper_bound))

    # Determine if any bucket of slopes is big enough
    return any(buckets > MIN_SLOPES_IN_BUCKET)
