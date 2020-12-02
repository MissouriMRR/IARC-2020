"""
For testing all module algorithms.
"""
import os, sys

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import unittest
import numpy as np
import cv2

from vision.module.in_frame import ModuleInFrame as mif
from vision.module.location import ModuleLocation
from vision.module.region_of_interest import region_of_interest
from vision.module.module_orientation import get_module_orientation


class TestModuleInFrame(unittest.TestCase):
    """
    Testing module.in_frame functionality.
    """

    def test_params(self):
        """
        Verify can handle range of input types.

        Parameters
        ----------
        image: ndarray
            Image to classify.
        """
        IMAGE_SIZE = [1920, 1080]

        ## 1 Channel Image
        with self.subTest(i="1 Channel Image"):
            pass

        ## 3 Channel [0, 1] Image
        with self.subTest(i="3 Channel [0, 1] Image"):
            pass

        ## 3 Channel {0..255} Image
        with self.subTest(i="3 Channel {0..255} Image"):
            color_image = np.ones(shape=(*IMAGE_SIZE, 3), dtype="uint8")

            result = mif(color_image)

            self.assertIn(result, [True, False])

        ## 4 Channel [0, 1] Image
        with self.subTest(i="4 Channel [0, 1] Image"):
            pass

        ## 4 Channel {0..255} Image
        with self.subTest(i="4 Channel {0..255} Image"):
            pass

        ## Empty image
        with self.subTest(i="Empty Image"):
            pass

        ## None as image
        with self.subTest(i="None as Image"):
            pass

    def test_return(self):
        """
        Verify returns only expected output types.

        Returns
        -------
        bool
        """
        ##
        for i in range(1, 6):
            color_image = 255 * np.ones((i * 100, i * 100, 3), dtype="uint8")
            color_image = cv2.circle(color_image, (i * 50, i * 50), 20, (0, 0, 0), 4)

            result = mif(color_image)

            self.assertIn(result, [True, False])

        ## Ensure does not modify original image
        color_image = 255 * np.ones((100, 100, 3), dtype="uint8")
        color_image = cv2.circle(color_image, (50, 50), 20, (0, 0, 0), 4)

        color_parameter = np.copy(color_image)

        mif(color_parameter)

        np.testing.assert_array_equal(color_image, color_parameter)


class TestModuleLocation(unittest.TestCase):
    """
    Testing ModuleLocation functionality.
    """

    def test_params(self):
        """
        Verify can handle range of input types.

        Parameters
        ----------
        image: ndarray
            Image to classify.
        """
        IMAGE_SIZE = [1920, 1080]

        ## 3 Channel {0..255} Image
        with self.subTest(i="3 Channel {0..255} Image"):
            color_image = np.ones(shape=(*IMAGE_SIZE, 3), dtype="uint8")
            depth_image = np.ones(shape=tuple(IMAGE_SIZE), dtype="uint8")

            locator = ModuleLocation()
            locator.img, locator.depth = color_image, depth_image
            result = locator.getCenter()

            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)

    def test_return(self):
        """
        Verify returns only expected output types.

        Returns
        -------
        bool
        """
        ## Straight line of circles
        for i in range(1, 6):
            color_image = 255 * np.ones((i * 100, i * 100, 3), dtype="uint8")
            depth_image = np.ones(shape=color_image.shape[:-1], dtype="uint8")
            for j in range(4):
                x, y = j * 50 + 50, j * 50 + 50
                color_image = cv2.circle(color_image, (x, y), 20, (0, 0, 0), 4)
                depth_image = cv2.circle(depth_image, (x, y), 20, 0, 4)

            locator = ModuleLocation()
            locator.img, locator.depth = color_image, depth_image
            result = locator.getCenter()

            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)

        ## Square
        for i in range(1, 6):
            color_image = 255 * np.ones((i * 100, i * 100, 3), dtype="uint8")
            depth_image = np.ones(shape=color_image.shape[:-1], dtype="uint8")
            for j in range(4):
                x, y = (j // 2 * 50) + 50, (j % 2 * 50) + 50
                color_image = cv2.circle(color_image, (x, y), 20, (0, 0, 0), 4)
                depth_image = cv2.circle(depth_image, (x, y), 20, 0, 4)

            locator = ModuleLocation()
            locator.img, locator.depth = color_image, depth_image
            result = locator.getCenter()

            self.assertIsInstance(result, tuple)
            self.assertEqual(len(result), 2)

        ## Ensure does not modify original image
        color_image = 255 * np.ones((100, 100, 3), dtype="uint8")
        color_image = cv2.circle(color_image, (50, 50), 20, (0, 0, 0), 4)
        depth_image = np.ones(shape=color_image.shape[:-1], dtype="uint8")

        color_parameter = np.copy(color_image)
        depth_parameter = np.copy(depth_image)

        locator = ModuleLocation()
        locator.img, locator.depth = color_parameter, depth_parameter
        result = locator.getCenter()

        np.testing.assert_array_equal(color_image, color_parameter)
        np.testing.assert_array_equal(depth_image, depth_parameter)


class TestModuleOrientation(unittest.TestCase):
    """
    Testing module.get_module_orientation for validity.
    """

    def test_params(self):
        """
        Verify can handle range of input type.

        Parameters
        ----------
        roi: ndarray
            module region of interest calculated by region_of_interest
        """
        IMAGE_SIZE = [1920, 1080]

        # testing with ndarray of all zeroes
        image = np.zeros(IMAGE_SIZE, dtype=int)
        result = get_module_orientation(image)

        self.assertIs(type(image), np.ndarray)
        self.assertIs(type(result), tuple)

    def test_get_module_orientation(self):

        img_dir = os.path.join(gparent_dir, "vision_images/module/Feb29")
        files = os.listdir(img_dir)

        # hand-picked images for unit test, assumes color-depth pair for each of the files
        estimates = {
            # FORMAT: "name_of_file_without_color-depth_tail" : [estimated_center (x, y), estimated_orientation (yaw, pitch)]
            "2020-02-29_15.35.31.313411": [(906, 807), (1, -25)],
            "2020-02-29_15.35.40.045632": [(641, 866), (15, -45)],
            "2020-02-29_15.35.57.551331": [(1228, 653), (-15, -1)],
            "2020-02-29_15.35.56.436446": [(1170, 644), (-10, 0)],
            "2020-02-29_15.40.42.462549": [(948, 620), (-20, -3)]
            # NOTE: The center tuples are estimated because center function does not work at the moment
            # TODO: Find more head-on shots of the module
        }

        for current_file in estimates.keys():
            # grabs and loadspair of color and depth files (assumes all files are in order of color1, depth1, color2, depth2, etc.)
            current_color_file = (
                os.path.join(img_dir, current_file) + "-colorImage.jpg"
            )  # current file
            current_color = cv2.imread(current_color_file)
            current_depth_file = (
                os.path.join(img_dir, current_file) + "-depthImage.npy"
            )  # next file over (after color img)
            current_depth = np.load(current_depth_file)

            # get center
            # loc = ModuleLocation()
            # loc.setImg(current_color, current_depth)
            # current_center = loc.getCenter(); #BROKEN
            current_center = estimates[current_file][0]

            # get region of interest
            roi = region_of_interest(
                current_depth,
                current_depth[current_center[1]][current_center[0]],
                current_center,
            )

            orientation = get_module_orientation(roi)

            estimated_pitch = estimates[current_file][1][0]
            estimated_yaw = estimates[current_file][1][1]
            calculated_pitch = orientation[0]
            calculated_yaw = orientation[1]

            self.assertTrue(
                estimated_pitch * 0.9 <= calculated_pitch <= estimated_pitch * 1.1
            )  # within ±10%
            self.assertTrue(
                estimated_yaw * 0.9 <= calculated_yaw <= estimated_yaw * 1.1
            )  # within ±10%

    def test_return(self):
        """
        Verify returns only expected output.

        Returns
        -------
        tuple
        """
        IMAGE_SIZE = [1920, 1080]

        # testing with ndarray of all zeroes
        image = np.zeros(IMAGE_SIZE, dtype=int)
        result = get_module_orientation(image)

        self.assertIs(type(result), tuple)


class TestRegionOfInterest(unittest.TestCase):
    """
    Testing module.region_of_interest for validity.
    """

    def test_params(self):
        """
        Verify can handle input types

        Parameters
        ----------
        depth_frame: ndarray
            The depth image.
        depth_val: float
            Measured value for the depth of the module from the camera.
        center: integer tuple
            Coordinates of the center of the module.
        """
        IMAGE_SIZE = [1920, 1080]

        # testing with ndarray of all zeroes, arbitrary depth value,
        #   and arbitrary center value
        depth_image = np.zeros(IMAGE_SIZE, dtype=int)
        depth_val = 300.0
        center = (300, 300)
        roi = region_of_interest(depth_image, depth_val, center)

        self.assertIs(type(depth_image), np.ndarray)
        self.assertIs(type(depth_val), float)
        self.assertIs(type(center), tuple)
        self.assertIs(type(roi), np.ndarray)

    def test_region_of_interest(self):
        img_dir = os.path.join(gparent_dir, "vision_images/module/Feb29")
        files = os.listdir(img_dir)

        # hand-picked images for unit test, only depth image is necessary
        estimates = {
            # FORMAT: "name_of_file_without_color-depth_tail" : [estimated_center (x, y), estimated_size{x,y)]
            "2020-02-29_15.48.10.480039": [(990, 600), (150, 200)],
            "2020-02-29_15.35.41.406247": [(830, 690), (120, 150)],
            "2020-02-29_15.35.57.551331": [(1228, 653), (90, 120)],
            "2020-02-29_15.35.56.436446": [(1170, 644), (145, 180)],
            "2020-02-29_15.40.42.462549": [(948, 620), (60, 70)]
            # NOTE: The center tuples are estimated because center function does not work at the moment
        }

        for current_file in estimates.keys():
            # grabs and loads depth file (assumes all files are in order of color1, depth1, color2, depth2, etc.)
            current_depth_file = (
                os.path.join(img_dir, current_file) + "-depthImage.npy"
            )
            current_depth_image = np.load(current_depth_file)

            # get center
            current_center = estimates[current_file][0]

            # get region of interest
            roi = region_of_interest(
                current_depth_image,
                current_depth_image[current_center[1]][current_center[0]],
                current_center,
            )

            estimated_height = estimates[current_file][1][1]
            estimated_width = estimates[current_file][1][0]
            calculated_height = roi.shape[0]
            calculated_width = roi.shape[1]

            self.assertTrue(
                estimated_height * 0.8 <= calculated_height <= estimated_height * 1.2
            )  # within ±20%
            self.assertTrue(
                estimated_width * 0.8 <= calculated_width <= estimated_width * 1.2
            )  # within ±20%

    def test_return(self):
        """
        Verify returns only expected output

        Returns
        -------
        ndarray
        """
        IMAGE_SIZE = [1920, 1080]

        # testing with ndarray of all zeroes, arbitrary depth value,
        #   and arbitrary center value
        depth_image = np.zeros(IMAGE_SIZE, dtype=int)
        arbitrary_value = 300
        roi = region_of_interest(depth_image, arbitrary_value, (arbitrary_value, arbitrary_value))

        self.assertIs(type(roi), np.ndarray)


if __name__ == "__main__":
    unittest.main()
