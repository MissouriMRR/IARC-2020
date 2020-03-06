"""
Runs through images and determines which have the pylon
"""
import os, sys
parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import unittest
import numpy as np

from vision.pylon.detect_pylon import detect_red
from vision.bounding_box import BoundingBox, ObjectType


class TestPylonClassifier(unittest.TestCase):
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
            color_image = np.random.randint(0, 255, size=(*IMAGE_SIZE, 3), dtype='uint8')

            result = detect_red(color_image, None)

            self.assertIsInstance(result, list)

            for box in result:
                self.assertIsInstance(box, BoundingBox)
                self.assertEqual(box.object_type, ObjectType.PYLON)

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
            color_image = np.random.randint(0, 255, size=(i * 100, i * 200, 3), dtype='uint8')

            result = detect_red(color_image, None)

            for box in result:
                self.assertIsInstance(box, BoundingBox, msg=f"{type(box)}")
                self.assertEqual(box.object_type, ObjectType.PYLON)
            
            if len(result):
                break
        else:
            self.fail("Failed to detect pylon in any sample image.")

        ## Ensure does not modify original image
        color_image = np.random.randint(0, 255, size=(i * 100, i * 200, 3), dtype='uint8')

        color_parameter = np.copy(color_image)

        detect_red(color_parameter, None)

        np.testing.assert_array_equal(color_image, color_parameter)


if __name__ == '__main__':
    unittest.main()
