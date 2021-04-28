"""
This file contains the ModuleInFrame function to detect if the module is in an image or not.

The commented-out lines are used to visualize the algorithm and are unnecessary for processing.

NOTE: File not maintained. See location.py for updated implementation.
"""
import cv2
import numpy as np
import argparse

# Constants
BLUR_SIZE = 5  # Blur kernel size
BUCKET_MODIFIER = 1  # Changes how many buckets are in the range
MIN_SLOPES_IN_BUCKET = (
    15  # Minimum number of slopes in a single bucket to identify the module
)
MAX_CIRCLES = 100  # Maximum number of cirlces that can be detected in an image before ModuleInFrame fails
MIN_CIRCLES = 4  # Minimum number of circles needed to perform calculations


def ModuleInFrame(color_image: np.ndarray) -> bool:
    """
    Determines if the Module is in frame

    Parameters
    ----------
    color_image: ndarray
        The color image.

    Returns
    -------
    bool: true if the module is in the frame and false if not in the frame
    """
    if color_image is None:
        raise ValueError(f"Image cannot be None.")

    # Ignore numpy warnings
    np.seterr(all="ignore")

    # Grayscale
    gray = cv2.cvtColor(src=color_image, code=cv2.COLOR_RGB2GRAY)

    # Guassian Blur
    blur = cv2.GaussianBlur(src=gray, ksize=(BLUR_SIZE, BLUR_SIZE), sigmaX=0)

    # Laplacian Transform
    laplacian = cv2.Laplacian(src=blur, ddepth=cv2.CV_8U, ksize=3)
    laplacian = np.uint8(laplacian)

    # Hough Circle Detection
    circles = cv2.HoughCircles(
        image=laplacian,
        method=cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=8,
        param1=75,
        param2=24,
        minRadius=0,
        maxRadius=50,
    )
    if (
        np.shape(circles)[0] < MIN_CIRCLES or np.shape(circles)[0] > MAX_CIRCLES
    ):  # too little or too many circles found
        return False

    circles = np.uint16(circles)

    # Resize circles into 2d array
    circles = np.reshape(circles, (np.shape(circles)[1], 3))

    # Finding slopes between the circles
    slopes = np.array([])
    for x, y, r in circles:
        # cv2.circle(output, (x, y), r, (0, 255, 0), 4)
        # cv2.rectangle(output, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)
        for iX, iY, iR in circles:
            m = (iY - y) / (iX - x)
            # slope must be non-infinite and can't be between the same circle
            if (not np.isnan(m)) and (not np.isinf(m)) and (x != iX and y != iY):
                slopes = np.append(slopes, m)

    if not slopes.size:
        return False

    # Converting slopes to degrees
    slopes = np.degrees(np.arctan(slopes))

    if not slopes.size:
        return False

    # Bucket sorting slopes to group parallels
    upper_bound = np.amax(slopes)
    lower_bound = np.amin(slopes)
    num_buckets = np.int32(upper_bound - lower_bound) * BUCKET_MODIFIER

    buckets, _ = np.histogram(slopes, num_buckets, (lower_bound, upper_bound))

    # show the output image
    # cv2.imshow("output", output)
    # cv2.waitKey(0)

    # Determine if any bucket of slopes is big enough
    return any(buckets > MIN_SLOPES_IN_BUCKET)


if __name__ == "__main__":
    """
    To test in_frame, use
    "python in_frame.py -i (image name).(image file extension)"

    Also note that in_frame, must be in the same file location,
    or a path must be specified
    """

    # # Create object for parsing command-line options
    parser = argparse.ArgumentParser(
        description='Read image file and display depth and test for ModuleInFrame.\
                                     To read an image file, type "python in_frame_driver.py --i (image name).(image extension)"'
    )
    # # Add argument which takes path to a bag file as an input
    parser.add_argument("-i", "--input", type=str, help="Path to the image file")
    # # Parse the command line arguments to an object
    args = parser.parse_args()

    if args.input:
        inputImageFile = args.input
    else:
        inputImageFile = "../vision_images/module/Block2.jpg"
        # raise FileNotFoundError("No input parameter has been given. For help type --help"

    image = cv2.imread(inputImageFile)
    npImage = np.asarray(image)

    print("Module in frame: " + str(ModuleInFrame(npImage)))
