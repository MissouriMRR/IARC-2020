
import cv2
import numpy as np
import argparse
import sys
import os

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

from obstacle import obstacle_finder
from vision.camera.bag_file import BagFile
# from obstacle.obstacle_finder import ObstacleFinder

BBOX_COLOR = (0, 255, 0)
BBOX_THICKNESS = 2


def get_params(**kwargs):
    """
    Generate a blob detector params object.
    """
    config = {
        "minThreshold": 10,
        "maxThreshold": 300,
        "filterByArea": True,
        "filterByConvexity": True,
        "filterByCircularity": True,
        "minCircularity": .005,
        "minConvexity": .87,
        "minArea": 100,
        "maxArea": 200000
    }
    config.update(kwargs)

    params = cv2.SimpleBlobDetector_Params()

    for key, value in config.items():
        setattr(params, key, value)

    return params


def plot_box(boxes, image, waittime=0):
    """
    Display BoundingBoxes on image.

    Parameters
    ----------
    boxes: list[BoundingBox]
        List of bounding boxes to plot on image.
    image: np.ndarray
        image to detect obstacles in
    waittime: int, default=0
        cv2.waitKey parameter, number of seconds to show window 0=inf.
    """
    if not isinstance(boxes, list):
        raise ValueError(f"Expected list of BoundingBox, got {type(boxes)} instead")
    if not isinstance(image, np.ndarray):
        raise ValueError(f"Expected argument of type ObstacleFinder, got {type(image)} instead")

    output = np.copy(image)  # Important so dont have to copy before passing here
    for bbox in boxes:
        if not bbox.vertices:
            continue
        print(bbox.vertices)
        X, Y = [], []
        for pair in bbox.vertices:
            x, y = pair[0], pair[1]

            x, y = int(x), int(y)

            X.append(x)
            Y.append(y)

        cv2.rectangle(output, (min(X), min(Y)), (max(X), max(Y)), BBOX_COLOR, BBOX_THICKNESS)
        #print('\tKeypoint:', bbox.pt[0], bbox.pt[1])

        #output = cv2.drawKeypoints(image, keypoints, outImage=np.array([]), color=(255, 0, 255), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    return output


if __name__ == '__main__':
    # # Create object for parsing command-line options
    parser = argparse.ArgumentParser(description="Read image file and display depth and test for ModuleInFrame.\
                                     To read an image file, type \"python in_frame_driver.py --i (image name).(image extension)\"")
    # # Add argument which takes path to a bag file as an input
    parser.add_argument("-i", "--input", type=str, help="Path to the image file")
    # # Parse the command line arguments to an object
    args = parser.parse_args()

    if args.input:
        video_file = args.input
    else:
        raise FileNotFoundError("No input parameter has been given. For help type --help")

    # image = cv2.imread(inputImageFile)
    # npImage = np.asarray(image)

    video = BagFile(100, 100, 60, video_file)

    finder = obstacle_finder.ObstacleFinder(params=get_params())

    cv2.namedWindow('Obstacle Detection', cv2.WINDOW_NORMAL)

    for depth, color in video:
        # # preprocessing the image
        # #   scales to 75% of original size, assuming 480x360, as the BAG files are.
        # #   NOTE: this may be different for direct camera feed, I think it's higher res
        # color = cv2.resize(color, dsize=(400, 360), interpolation=cv2.INTER_CUBIC)
        # #   blurring image
        # color = cv2.blur(color, (5, 5))
        # #   converts to greyscale
        # # color = cv2.cvtColor(color, cv2.COLOR_BGR2GRAY)
        # #   increases contrast
        # #   NOTE: has to convert from float64 back to uint8, which seems not to lead to
        # #           the implied result of multiplying the contrast by 1.2
        # #         whole numbers seem to work better
        # # color = 1.2 * color
        # # color = color.astype(np.uint8)
        # # color = 2 * color

        # depth = ((depth / np.max(depth)) * 255)
        # greyscaleDepth = cv2.convertScaleAbs(depth)
        # boundingBoxes = finder.find(greyscaleDepth, None)
        # result = plot_box(boundingBoxes, greyscaleDepth)

        boundingBoxes = finder.find(color, None)
        result = plot_box(boundingBoxes, color)
        cv2.imshow('Obstacle Detection', result)
        cv2.waitKey(1)
