"""
This file contains the ModuleInFrame function to detect if the module is in an image
"""

import cv2
import numpy as np

def ModuleInFrame(imgPath):
    """
    Determines if the Module is in frame

    Parameters
    ----------
    imgPath, is a string that is the path of the image to be passed into the function

    Returns
    -------
    isInFrame, a bool, which is true if the module is in the frame and false if not in the frame
    """

    # Ignore numpy warnings
    np.seterr(all="ignore")

    # Get target image
    img = cv2.imread(imgPath)

    # Remove depth channel
    img.reshape((-1, 3))

    # Grayscale
    gray = cv2.cvtColor(src=img, code=cv2.COLOR_RGB2GRAY)

    # Guassian Blur
    blur = cv2.GaussianBlur(src=gray, ksize=(5,5), sigmaX=0)

    # Laplacian Transform
    laplacian = cv2.Laplacian(src=blur, ddepth=cv2.CV_8U, ksize=3)
    laplacian = np.uint8(np.around(laplacian))

    # Hough Circle Detection
    circles = cv2.HoughCircles(image=laplacian, method=cv2.HOUGH_GRADIENT, dp=1, minDist=8, param1=50, param2=40, minRadius=0, maxRadius=50)
    circles = np.uint16(np.around(circles))

    # Finding slopes between the circles
    slopes = { }
    for circle in circles:
        for (x, y, r) in circle:
            for iCircle in circles:
                for (iX, iY, iR) in iCircle:
                    m = (iY - y) / (iX - x)
                    if(m not in slopes):
                        slopes[m] = 0
                    slopes[m] += 1

    # Counting the number of parallel slopes
    parallels = 0
    for(key, val) in slopes.items():
        if(val > 1):
            parallels += val
        for (key2, val2) in slopes.items():
            if(abs(key - key2) < .01 and key != key2):
                parallels += 1

    # Determine if module is in frame
    isInFrame = False
    if(parallels > 300):
        isInFrame = True
    return isInFrame