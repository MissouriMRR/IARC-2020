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
        self.text = np.array(["модули", "иртибот"])
        self.tessdata: dict = {}

    def detect_russian_word(
        self, color_image: np.ndarray, depth_image: np.ndarray
    ) -> list:
        """
        Detect words in given image.

        Parameters
        ------
        color_image: np.ndarray
            3-channel color image to perform text detection on
        depth_image: np.ndarray
            1-channel depth image from the realsense camera

        Returns
        -------
        list[BoundingBox] - A list of rotated bounding box objects that contain desired text
            Note that there may be different bounding boxes for each word
        """
        self.tessdata: dict = {}

        (
            sliced_rotated_image,
            x_ul,
            y_ul,
            rotated_angle,
        ) = self._get_rotated_min_area_rect(color_image, depth_image)

        if len(sliced_rotated_image) == 0:
            return []

        self.tessdata = pytesseract.image_to_data(
            sliced_rotated_image, output_type=pytesseract.Output.DICT, lang="uzb_cyrl"
        )

        detected_words = self.tessdata["text"]
        box_obs = []

        rows, columns, _ = color_image.shape
        theta = -rotated_angle  # angle to rotate text boxes back to original position

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
                ll_pt = (x, y + h)  # lower left point of rotated rectangle
                ul_pt = (x, y)  # upper left point of rotated rectangle
                ur_pt = (x + w, y)  # upper right point of rotated rectangle
                lr_pt = (x + w, y + h)  # lower right point of rotated rectangle

                # text detection is performed on a rotated image
                # boxes need to be rotated back to their original position
                rotated_verts = np.array([[ll_pt, ul_pt, ur_pt, lr_pt]])

                # rotate box back to original point on color image
                rot_mat = cv2.getRotationMatrix2D(
                    center=(x_ul, y_ul), angle=theta, scale=1
                )
                verts = cv2.transform(src=rotated_verts, m=rot_mat)[0]
                verts = [
                    (int(row), int(col)) for (row, col) in verts
                ]  # cast for proper types from ndarray

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
        color_image: np.ndarray
            color ndarray from the realsense camera
        depth_image: np.ndarray
            depth ndarray from the realsense camera

        Returns
        --------
        tuple - (minAreaRect, x_ul, y_ul, angle)

            minAreaRect: np.ndarray
                rotated ndarray of the largest contour
            x_ul: int
                x-coordinate of upper-left corner of minAreaRect relative to color_image
            y_ul: int
                y-coordinate of upper-left corner of minAreaRect relative to color_image
            angle: float
                angle that the minAreaRect is rotated relative to color_image
        """
        BLUR_SIZE = 5  # size of blur kernel
        MIN_BLUE = 15  # minimum blue value in the image
        RED_WT = 1.7  # blue-red weight ratio threshold
        GREEN_WT = 1.1  # blue-green weight ratio threshold
        DEPTH_THRESH = 8000  # maximum depth for background filtering
        EDGE_LOWER = 250  # lower bound gradient threshold for edge detection
        EDGE_UPPER = 255  # upper bound gradient threshold for edge detection

        # the text is always in a blue rectangle. this finds the rectangle
        # remove noise, int16 to prevent negative overflow in following step
        blur_image = np.int16(cv2.GaussianBlur(src=color_image, ksize=(5, 5), sigmaX=0))
        b_image, g_image, r_image = (
            blur_image[:, :, 0],
            blur_image[:, :, 1],
            blur_image[:, :, 2],
        )  # separate channels

        r_image = np.where(r_image == 0, 1, r_image)  # prevent division by zero
        g_image = np.where(g_image == 0, 1, g_image)  # prevent division by zero

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
        # canny is too good at its job, soften it up a bit for houghlines and findcontours
        edges = cv2.GaussianBlur(src=edges, ksize=(BLUR_SIZE, BLUR_SIZE), sigmaX=0)

        # specifically getting a 2-tier contour
        # our target is the blue rectangle surrounding the text
        # the rectangle has an inside and outside boundary, and we can use that fact to eliminate noise
        # that is, any contours that don't have child contours aren't our rectangle
        contours, hierarchy = cv2.findContours(
            image=edges, mode=cv2.RETR_CCOMP, method=cv2.CHAIN_APPROX_NONE
        )

        if hierarchy is None:
            return (np.array([]), 0, 0, 0)

        contourAreas = np.array([cv2.contourArea(c) for c in contours])
        largestContour = contours[np.argmax(contourAreas)]

        x, y, w, h = cv2.boundingRect(largestContour)

        rect = cv2.minAreaRect(largestContour)

        center, size, theta = rect

        ## WORKAROUND for potential bug on linux build of opencv library ##
        # BUG: opencv implements new undocumented implementation of cv2.minAreaRect return value
        #      where angle is in range (0, 90] on Linux but is in range (-90, 0] on Windows
        #      GitHub Issue #19472: https://github.com/opencv/opencv/issues/19472
        theta = theta - 90 if 0 < theta <= 90 else theta

        x_ul = int(center[0] - (size[0] / 2))
        y_ul = int(center[1] - (size[1] / 2))

        # adjust angle so the image isn't corrected to a 90 degree angle
        if theta > -45:
            rotation_angle = theta
        else:
            rotation_angle = theta + 90

        rows, columns, _ = color_image.shape
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

        return sliced_rotated_image, x_ul, y_ul, rotation_angle

    def visualize_min_area_rect(
        self, color_image: np.ndarray, depth_image: np.ndarray
    ) -> None:
        """
        Allows for visualization of the rotated min area rect detect_words is using

        Parameters
        -----
        color_image: np.ndarray
            color ndarray from the realsense camera
        depth_image: np.ndarray
            depth ndarray from the realsense camera

        Returns
        -----
        None
        """
        sliced_rotated_image, _, _, _ = self._get_rotated_min_area_rect(
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
