import unittest
import os
from vision.blob.blobfind import find_blobs

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
        found_blobs = []
        vision_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        for i, img in enumerate(os.listdir('../blob/samples')):
            with self.subTest(i=img):
                img_file = os.path.join(vision_folder, 'blob', 'samples', img)
                keypoints = find_blobs(img_file, logging=True)
                self.assertEqual(len(keypoints), expected_blobs[i], msg=f"Expected {expected_blobs[i]} blobs, found {len(keypoints)} in image {img}")

if __name__ == '__main__':
    unittest.main()
