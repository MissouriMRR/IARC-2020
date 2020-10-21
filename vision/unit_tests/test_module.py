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

# from vision.module.detector import ModuleKMeans as mkm


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

            result = mif(color_image, None)

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

            result = mif(color_image, None)

            self.assertIn(result, [True, False])

        ## Ensure does not modify original image
        color_image = 255 * np.ones((100, 100, 3), dtype="uint8")
        color_image = cv2.circle(color_image, (50, 50), 20, (0, 0, 0), 4)

        color_parameter = np.copy(color_image)

        mif(color_parameter, None)

        np.testing.assert_array_equal(color_image, color_parameter)


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
        image = np.zeros(IMAGE_SIZE)
        result = get_module_orientation(image)

        self.assertIs(type(image), np.ndarray)
        self.assertIs(type(result), tuple)

    def test_get_module_orientation(self):

        img_dir = os.path.join(gparent_dir, "vision_images/module/Feb29")
        files = os.listdir(img_dir)

        # hand-picked images for unit test, assumes color-depth pair for each of the files
        estimates = {
            # FORMAT: "name_of_file_without_color-depth_tail" : [estimated_center, estimated_orientation]
            "2020-02-29_15.35.31.313411": [(906, 807), (-25, -1)],
            "2020-02-29_15.35.40.045632": [(641, 866), (-70, -25)],
            "2020-02-29_15.35.57.551331": [(1228, 653), (0, 5)],
            "2020-02-29_15.35.56.436446": [(1170, 644), (10, 10)],
            "2020-02-29_15.40.42.462549": [(948, 620), (20, 5)]
            # NOTE: The center tuples are estimated because center function does not work at the moment
            # TODO: Find more head-on shots of the module
        }

        counter = 0
        for current_file in files:
            counter += 1  # started one ahead to get next (depth) file
            stripped_filename = current_file[:26]

            # Get files two at a time, color w/ depth
            if (
                counter - 1
            ) % 2 == 0 and stripped_filename in estimates:  # counts every other file and checks if current is in estimates

                # grabs and loadspair of color and depth files (assumes all files are in order of color1, depth1, color2, depth2, etc.)
                current_color_file = os.path.join(img_dir, current_file)  # current file
                current_color = cv2.imread(current_color_file)
                current_depth_file = files[counter]  # next file over (after color img)
                current_depth = np.load(os.path.join(img_dir, current_depth_file))

                # get center and get and show region of interest as image
                current_center = estimates[stripped_filename][0]
                loc = ModuleLocation()
                loc.setImg(current_color, current_depth)
                # current_center = loc.getCenter(); #BROKEN

                # get region of interest
                roi = region_of_interest(
                    current_depth,
                    current_depth[current_center[1]][current_center[0]],
                    current_center,
                )

                orientation = get_module_orientation(roi)

                estimated_pitch = estimates[stripped_filename][1][0]
                estimated_yaw = estimates[stripped_filename][1][1]
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
        image = np.zeros(IMAGE_SIZE)
        result = get_module_orientation(image)

        self.assertIs(type(result), tuple)


if __name__ == "__main__":
    unittest.main()
