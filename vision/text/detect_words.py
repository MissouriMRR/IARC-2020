"""
This program grabs text from an image and compares it with 'модули иртибот'.
Nominal function returns a lsit of bounding boxes containing the desired text
"""
import pytesseract
import numpy as np
import cv2
import os, sys

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

from bounding_box import BoundingBox, ObjectType


class TextDetector:
    """
    Finds the bounding boxes of the specified text in the frame.
    """

    def __init__(self):
        self.text = np.array(["модули", "иртибот"]) # Words that will appear on the mast
        self.tessdata: dict = {} # Text detected by pytesseract

    def detect_russian_word(
        self, color_image: np.ndarray, depth_image: np.ndarray
    ) -> list:
        """
        Detect words in given image.

        Paramters
        ------
        color_image
            color ndarray from the realsense camera
        depth_image
            depth ndarray from the realsense camera

        Returns
        -------
        A list of bounding box objects that contain desired text
            Note that there may be different bounding boxes for each word
        """
        self.tessdata: dict = {}

        # Get the sliced image to attempt text detection on
        sliced_rotated_image, x_ul, y_ul = self._get_rotated_min_area_rect(
            color_image, depth_image
        )

        if sliced_rotated_image.size == 0: # rotated image was not found
            return []

        # Text detection
        self.tessdata = pytesseract.image_to_data(
            sliced_rotated_image, output_type=pytesseract.Output.DICT, lang="uzb_cyrl"
        )

        detected_words = self.tessdata["text"]
        box_obs = []

        # Search for words that will appear on mast in detected text
        for i, det_word in enumerate(detected_words):
            if not det_word:
                continue  # ignore empty strings

            # if any of the words are in the detected words, add BoundingBox to final set
            # This is done to allow cases where extra characters around the words are detected
            if np.any([(rus_word in det_word.lower()) for rus_word in self.text]):
                (x, y, w, h) = (
                    self.tessdata["left"][i] + x_ul,
                    self.tessdata["top"][i] + y_ul,
                    self.tessdata["width"][i],
                    self.tessdata["height"][i],
                )
                verts = [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]
                box = BoundingBox(verts, ObjectType("text"))
                box_obs.append(box)

        return box_obs

    def _get_rotated_min_area_rect(
        self, color_image: np.ndarray, depth_image: np.ndarray
    ) -> tuple:
        """
        Returns min area rect of inside the tape

        Parameters
        -----
        color_image
            color ndarray from the realsense camera
        depth_image
            depth ndarray from the realsense camera

        Returns
        --------
        tuple - (minAreaRect, x_ul, y_ul)
            minAreaRect: np.ndarray
                rotated ndarray of the largest contour
            x_ul: int
                x-coordinate of upper-left corner of minAreaRect relative to color_image
            y_ul: int
                y-coordinate of upper-left corner of minAreaRect relative to color_image
        """
        # Constants for cv2 functions
        BLUR_SIZE = 5  # size of blur kernel
        MIN_BLUE = 15  # minimum blue value in the image
        RED_WT = 1.7  # blue-red weight ratio threshold
        GREEN_WT = 1.1  # blue-green weight ratio threshold
        DEPTH_THRESH = 8000  # maximum depth for background filtering
        EDGE_LOWER = 250  # lower bound gradient threshold for edge detection
        EDGE_UPPER = 255  # upper bound gradient threshold for edge detection

        # the text is always in a blue rectangle. this finds the rectangle
        # cast to int16 to prevent negative overflow in following steps
        blur_image = np.int16(cv2.GaussianBlur(src=color_image, ksize=(BLUR_SIZE, BLUR_SIZE), sigmaX=0))
        
        # Separate BGR channels
        b_image, g_image, r_image = (
            blur_image[:, :, 0],
            blur_image[:, :, 1],
            blur_image[:, :, 2],
        )  

        # prevent division by zero
        r_image = np.where(r_image == 0, 1, r_image)  
        g_image = np.where(g_image == 0, 1, g_image)

        # Find blue pixels
        blue_mask = np.logical_and(
            (b_image / r_image > RED_WT),
            (b_image / g_image > GREEN_WT),
            (b_image > MIN_BLUE),  # eliminate near-black pixels
        )

        # make blue parts black, rest white
        mask_image = np.where(blue_mask, np.uint8(0), np.uint8(255))

        # filter out background with depth image
        mask_image = np.where((depth_image < DEPTH_THRESH), mask_image, np.uint8(255))

        # apply edge detection
        edges = cv2.Canny(
            image=mask_image, threshold1=EDGE_LOWER, threshold2=EDGE_UPPER
        )

        # Soften for findContours
        edges = cv2.GaussianBlur(src=edges, ksize=(BLUR_SIZE, BLUR_SIZE), sigmaX=0)

        # specifically getting a 2-tier contour
        # our target is the blue rectangle surrounding the text
        contours, hierarchy = cv2.findContours(
            image=edges, mode=cv2.RETR_CCOMP, method=cv2.CHAIN_APPROX_NONE
        )

        # the rectangle has an inside and outside boundary, and we can use that fact to eliminate noise
        # that is, any contours that don't have child contours aren't our rectangle
        if hierarchy is None:
            return np.array([]), 0, 0

        # Find the largest contour
        contourAreas = np.array([cv2.contourArea(c) for c in contours])
        largestContour = contours[np.argmax(contourAreas)]

        x, y, w, h = cv2.boundingRect(largestContour)

        rect = cv2.minAreaRect(largestContour)

        center, size, theta = rect

        # theta = theta - 90 #NOTE: comment this line out if running code on Windows

        x_ul = center[0] - (size[0] / 2)
        y_ul = center[1] - (size[1] / 2)

        # adjust angle so the image isn't corrected to a 90 degree angle
        if abs(theta) > 45:
            rotation_angle = -(90 - theta)
        else:
            rotation_angle = theta

        # normalize the portion of the image with the rectangle
        rows, columns = color_image.shape[0], color_image.shape[1]
        matrix = cv2.getRotationMatrix2D(
            center=(columns / 2, rows / 2), angle=rotation_angle, scale=1
        )
        rotated = cv2.warpAffine(src=color_image, M=matrix, dsize=(columns, rows))

        rect0 = (rect[0], rect[1], 0.0)
        box = cv2.boxPoints(rect0)
        points = np.int0(cv2.transform(np.array([box]), matrix))[0]
        points[points < 0] = 0

        sliced_rotated_image = rotated[
            points[1][1] : points[0][1], points[1][0] : points[2][0]
        ]

        return sliced_rotated_image, x_ul, y_ul

    def visualize_min_area_rect(
        self, color_image: np.ndarray, depth_image: np.ndarray
    ) -> None:
        """
        Allows for visualization of the rotated min area rect detect_words is using

        Parameters
        -----
        color_image
            color ndarray from the realsense camera
        depth_image
            depth ndarray from the realsense camera

        Returns
        -----
        None
        """
        sliced_rotated_image, _, __ = self._get_rotated_min_area_rect(
            color_image, depth_image
        )

        cv2.imshow("MinAreaRect", sliced_rotated_image)
        cv2.waitKey(0)


if __name__ == "__main__":
    import time
    import os
    import argparse
    from common import box_plotter

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

    color_image = cv2.imread(inputImageFile + "-colorImage.jpg")
    depth_image = np.load(inputImageFile + "-depthImage.npy")

    if color_image is None:
        raise FileNotFoundError("Could not read image!")

    detector = TextDetector()
    detector.visualize_min_area_rect(color_image, depth_image)
    result = detector.detect_russian_word(color_image, depth_image)
    print(result)

    # box_plotter.plot_box(result, color_image)
