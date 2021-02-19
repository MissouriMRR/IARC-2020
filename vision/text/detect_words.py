"""
This program grabs text from an image and compares it with 'модули иртибот'.
It returns 'Match' if it identifies 'модули иртибот' and 'Not Match' when it doesnt.
"""
import pytesseract
import numpy as np
import cv2
import os, sys

pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files/Tesseract-OCR/tesseract.exe'

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

    def detect_russian_word(self, color_image: np.ndarray, depth_image: np.ndarray):
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
        """
        sliced_rotated_image = self.get_rotated_min_area_rect(color_image, depth_image)

        if sliced_rotated_image == []:
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
                        cv2.rectangle(color_image, verts[0], verts[-1], (0, 255, 0), 2)
                        box = BoundingBox(verts, ObjectType("text"))
                        box_obs.append(box)
                        break

        return box_obs


    def get_rotated_min_area_rect(self, color_image: np.ndarray, depth_image: np.ndarray):
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
        min area rect
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

        largestArea = 0
        largestContour = 0
        for c in contours:
            if cv2.contourArea(c) > largestArea:
                largestContour = c

        # contourAreas = np.array([cv2.contourArea(c) for c in contours])
        # largestContour = contours[np.argmax(contourAreas)]

        x,y,w,h = cv2.boundingRect(largestContour)

        rect = cv2.minAreaRect(largestContour)

        center, size, theta = rect
        
        # adjust angle so the image isn't corrected to a 90 degree angle
        if abs(theta) > 45:
            if theta < 0:
                theta = 90 + theta
            else:
                theta = 90 - theta

        # rotates/slices image to min area rect of largest contour
        center, size = tuple(map(int, center)), tuple(map(int, size))
        rot_matrix = cv2.getRotationMatrix2D(center, theta, 1)
        dst = cv2.warpAffine(color_image, rot_matrix, color_image.shape[:2])
        sliced_rotated_image = cv2.getRectSubPix(dst, size, center)

        return sliced_rotated_image


    def visualize_min_area_rect(self, color_image: np.ndarray, depth_image: np.ndarray):
        """
        Allows for visualization of the rotated min area rect detect_words is using

        Parameters
        -----
        color_image
            color ndarray from the realsense camera
        depth_image
            depth ndarray from the realsense camera
        """
        sliced_rotated_image = self.get_rotated_min_area_rect(color_image, depth_image)

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