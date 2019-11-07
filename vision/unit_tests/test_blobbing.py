import unittest
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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
        expected_blobs: list[int]
            expected blobs to be found in each image

        Returns
        -------
        list[bool]
            whether the expected number of blobs in each image equals the detected number of blobs
        """
        expected_blobs = [1, 30, 1, 1]
        vision_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        for i, img in enumerate(os.listdir('../blob/samples')):
            with self.subTest(i=img):
                img_file = os.path.join(vision_folder, 'blob', 'samples', img)
                detector = BlobFinder(img_file)
                bounding_boxes = detector.find()
                self.assertEqual(len(bounding_boxes), expected_blobs[i], msg=f"Expected {expected_blobs[i]} blobs, found {len(bounding_boxes)} in image {img}")

if __name__ == '__main__':
    unittest.main()
