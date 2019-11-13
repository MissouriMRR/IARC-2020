import unittest
import os
import sys
import cv2
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from vision.blob.blobfind import BlobFinder
except ImportError:
    from blob.blobfind import BlobFinder

class TestBlobbing(unittest.TestCase):
    def test_finding_blobs(self):
        """
        Tests that the expected number of blobs is found

        Settings
        --------
        expected_blobs: dict{string: int}
            number of expected blobs (value) to be found in each image (key)

        Returns
        -------
        list[bool]
            whether the expected number of blobs in each image equals the detected number of blobs
        """
        expected_blobs = {
            "apple.jpg": 1,
            "legos.jpg": 30,
            "MyBeach.png": 1,
            "oranges.png": 1,
            "sampleobj.png": 1
        }
        vision_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        for filename, expected in expected_blobs.items():
            with self.subTest(i=filename):
                img_file = os.path.join(vision_folder, 'blob', 'samples', filename)
                img_file = cv2.imread(img_file)
                detector = BlobFinder(img_file)
                bounding_boxes = detector.find()
                self.assertEqual(len(bounding_boxes), expected_blobs[filename], msg=f"Expected {expected_blobs[filename]} blobs, found {len(bounding_boxes)} in image {filename}")

if __name__ == '__main__':
    unittest.main()
