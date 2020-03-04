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
#from vision.module.detector import ModuleKMeans as mkm


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
            color_image = np.ones(shape=(*IMAGE_SIZE, 3), dtype='uint8')

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
            color_image = 255 * np.ones((i * 100, i * 100, 3), dtype='uint8')
            color_image = cv2.circle(color_image, (i * 50, i * 50), 20, (0, 0, 0), 4)

            result = mif(color_image, None)

            self.assertIn(result, [True, False])

        ## Ensure does not modify original image
        color_image = 255 * np.ones((100, 100, 3), dtype='uint8')
        color_image = cv2.circle(color_image, (50, 50), 20, (0, 0, 0), 4)

        color_parameter = np.copy(color_image)

        mif(color_parameter, None)

        np.testing.assert_array_equal(color_image, color_parameter)


if __name__ == '__main__':
    unittest.main()
