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
        self.text = "модулииртибот"

    def detect_russian_word(self, color_image: np.ndarray, depth_image: np.ndarray) -> list:
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
        sliced_rotated_image = self._get_rotated_min_area_rect(color_image, depth_image)

        if len(sliced_rotated_image) == 0:
            return []

        tessdata = pytesseract.image_to_data(
            sliced_rotated_image, output_type=pytesseract.Output.DICT, lang="uzb_cyrl"
        )

        n_boxes = len(tessdata["level"])
        box_obs = []
        contents = tessdata["text"]
        for i in range(n_boxes):
            if not contents[i]:
                continue
            else:
                for j in contents[i]:
                    if j in self.text:
                        (x, y, w, h) = (
                            tessdata["left"][i],
                            tessdata["top"][i],
                            tessdata["width"][i],
                            tessdata["height"][i],
                        )
                        verts = [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]
                        box = BoundingBox(verts, ObjectType("text"))
                        box_obs.append(box)
                        break

        return box_obs


    def _get_rotated_min_area_rect(self, color_image: np.ndarray, depth_image: np.ndarray) -> np.ndarray:
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
        min area rect: np.ndarray
            rotated ndarray of the largest contour
        """
        # the text is always in a blue rectangle. this finds the rectangle
        # remove noise, int16 to prevent negative overflow in following step
        blur_image = np.int16(cv2.GaussianBlur(color_image, (5, 5), 0))
        b_image, g_image, r_image = (
            blur_image[:, :, 0],
            blur_image[:, :, 1],
            blur_image[:, :, 2],
        )  # separate channels

        isblue = np.logical_and((b_image - r_image > 120), (b_image - g_image > 20))

        # make blue parts black, rest white
        mask_image = np.where(isblue, np.uint8(0), np.uint8(255))

        mask_image = np.where((depth_image < 8000), mask_image, np.uint8(255))

        edges = cv2.Canny(mask_image, 250, 255)
        # canny is too good at its job, soften it up a bit for houghlines and findcontours
        edges = cv2.GaussianBlur(edges, (5, 5), 0)

        # specifically getting a 2-tier contour
        # our target is the blue rectangle surrounding the text
        # the rectangle has an inside and outside boundary, and we can use that fact to eliminate noise
        # that is, any contours that don't have child contours aren't our rectangle
        contours, hierarchy = cv2.findContours(
            edges, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_NONE
        )

        if hierarchy is None:
            return []

        contourAreas = np.array([cv2.contourArea(c) for c in contours])
        largestContour = contours[np.argmax(contourAreas)]

        x,y,w,h = cv2.boundingRect(largestContour)

        rect = cv2.minAreaRect(largestContour)

        center, size, theta = rect
        
        # adjust angle so the image isn't corrected to a 90 degree angle
        if abs(theta) > 45:
            if theta < 0:
                theta = 90 + theta
            else:
                theta = 90 - theta

        rows, columns = color_image.shape[0], color_image.shape[1]
        matrix = cv2.getRotationMatrix2D((columns/2, rows/2), theta, 1)
        rotated = cv2.warpAffine(color_image, matrix, (columns, rows))

        rect0 = (rect[0], rect[1], 0.0) 
        box = cv2.boxPoints(rect0)
        points = np.int0(cv2.transform(np.array([box]), matrix))[0]    
        points[points < 0] = 0

        sliced_rotated_image = rotated[points[1][1]:points[0][1], 
                                       points[1][0]:points[2][0]]

        return sliced_rotated_image


    def visualize_min_area_rect(self, color_image: np.ndarray, depth_image: np.ndarray) -> None:
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
        sliced_rotated_image = self._get_rotated_min_area_rect(color_image, depth_image)

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
    print (result)

    # box_plotter.plot_box(result, mask_image)