"""
Runs through images and determines which have the pylon
"""

import unittest
import os
import sys
import json
import cv2

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

# from vision.pylon.detect_pylon import import_params
from vision.pylon.detect_pylon import detect_red

class TestPylon(unittest.TestCase):
    def test_pylon(self):
        """
        Tests whether or not the pylon's red is detected in the image

        Settings
        --------
        expected_blobs: dict{string: int}
            number of expected blobs (value) to be found in each image (key)

        Returns
        -------
        list[bool]
            whether the expected number of blobs in each image equals the detected number of blobs
        """
        expected_pylon = {
            "sim_pylon.png":True,
            "sim_pylon2.png":True,
            "sim_pylon3.png":True
        }
        prefix = 'vision' if os.path.isdir("vision") else '..'

        for filename, expected in expected_pylon.items():
            with self.subTest(i=filename):
                img_filename = os.path.join(prefix, 'vision_images', 'pylon', filename)
                img_file = cv2.imread(img_filename)
                if img_file is None:
                    self.fail(msg="Failed to read image.  " + img_filename)

                # detector = ObstacleFinder(img_file, params=config)
                # bounding_boxes = detector.find()
                pylon = detect_red(img_file)

                self.assertEqual(pylon, expected, msg=f"Expected {expected} blobs, did not find pylon in image {filename}")


if __name__ == '__main__':
    unittest.main()
