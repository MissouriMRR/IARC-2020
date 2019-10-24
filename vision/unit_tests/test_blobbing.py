import unittest
import os
import numpy as np
from vision.blob.blobfind import find_blobs

class TestBlobbing(unittest.TestCase):
    def test_finding_blobs(self):
        """
        Tests that the expected number of blobs is found

        Settings
        --------
        :var samples_directory: relative path to a directory of sample images
        :var expected_blobs: list of expected blobs to be found in each image

        Returns
        -------
        :return ndarray[bool] Whether each image in has the correct number of
        """
        samples_directory = '../blob/samples'
        expected_blobs = np.array([1, 30, 1, 1])
        found_blobs = np.array([])
        for i, img in enumerate(os.listdir(samples_directory)):
            img_file = samples_directory + os.fsdecode(img)
            keypoints = find_blobs(img_file)
            np.append(found_blobs, len(keypoints))
        self.assertLessEqual(list(expected_blobs), list(found_blobs))


if __name__ == '__main__':
    unittest.main()