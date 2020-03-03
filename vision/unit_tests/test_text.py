"""
Text related unit tests.
"""
import sys, os
parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import unittest
import numpy as np
import cv2

from text.detect_words import detect_russian_word
from bounding_box import BoundingBox, ObjectType


class TestDetectRussianWord(unittest.TestCase):
    """
    Testing the text detector.
    """
    def test_detect_russian(self):
        """
        Testing text_detector.

        Parameters
        ----------
        image: ndarray

        Settings
        --------
        _params: cv2.SimpleBlobDetector_Params
            Parameters for blob_detector.
        blob_detector: cv2.SimpleBlobDetector_create(self.params)
            Blob detection algorithm.

        Returns
        -------
        list[BoundingBox]
        """
        ### Ensure range of Parameters work
        IMAGE_SIZE = (1920, 1080)

        ## 3 Channel {0..255} Image
        with self.subTest(i="3 Channel {0..255} Image"):
            color_image = np.random.randint(0, 255, size=(*IMAGE_SIZE, 3), dtype='uint8')

            detect_russian_word(color_image, None)

        ### Ensure returns correct type of BoundingBox
        with self.subTest(i="Object type"):
            color_image = np.zeros((1000, 1000, 3), dtype='uint8')
            cv2.putText(color_image, "Read Me", (200, 200), cv2.FONT_HERSHEY_SIMPLEX, 2, 255)

            output = detect_russian_word(color_image, None)

            if output is None:
                self.fail(msg="Failed to detect obstacle to be able to test.")

            for box in output:
                self.assertIsInstance(box, BoundingBox)

                ##
                self.assertIn(len(box.vertices), [4, 8])

                X, Y = [], []
                for vertex in box.vertices:
                    self.assertIsInstance(vertex, tuple)

                    X.append(vertex[0])
                    Y.append(vertex[1])

                self.assertGreater(max(X) - min(X), 50)
                self.assertGreater(max(Y) - min(Y), 50)

                ##
                self.assertIsInstance(box.object_type, ObjectType)
                self.assertEqual(box.object_type, ObjectType.TEXT)


if __name__ == '__main__':
    unittest.main()
