"""
Obstacle detector unit tests.
"""
import os, sys
parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import unittest

import numpy as np
import cv2

from vision.obstacle.obstacle_finder import ObstacleFinder
from vision.bounding_box import BoundingBox, ObjectType


class TestObstacleDetection(unittest.TestCase):
    """
    Testing obstacle detection.
    """
    @staticmethod
    def _get_params(**kwargs):
        """
        Generate a blob detector params object.
        """
        config = {
            "minThreshold": 10,
            "maxThreshold": 300,
            "filterByArea": True,
            "minArea": 100,
            "maxArea": 200000
        }
        config.update(kwargs)

        params = cv2.SimpleBlobDetector_Params()

        for key, value in config.items():
            setattr(params, key, value)

        return params

    def test_find(self):
        """
        Testing ObstacleFinder.find.

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
            detector = ObstacleFinder(params=self._get_params())

            color_image = np.random.randint(0, 255, size=(*IMAGE_SIZE, 3), dtype='uint8')

            detector.find(color_image, None)

        ### Ensure returns correct type of BoundingBox
        with self.subTest(i="Object type"):
            detector = ObstacleFinder(params=self._get_params())

            for i in range(1, 9):
                color_image = np.zeros((1000, 1000, 3), dtype='uint8')
                cv2.rectangle(color_image, (200, 200), (200 + (i * 100), 200 + (i * 100)), (255, 255, 255), 2)

                output = detector.find(color_image, None)

                if output is not None:
                    break
            else:
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
                self.assertEqual(box.object_type, ObjectType.AVOID)

        ## Ensure does not modify original image
        detector = ObstacleFinder(params=self._get_params())

        color_image = np.zeros((1000, 1000, 3), dtype='uint8')
        cv2.rectangle(color_image, (200, 200), (200 + (i * 100), 200 + (i * 100)), (255, 255, 255), 2)

        color_parameter = np.copy(color_image)

        detector.find(color_parameter, None)

        np.testing.assert_array_equal(color_image, color_parameter)


if __name__ == '__main__':
    unittest.main()
