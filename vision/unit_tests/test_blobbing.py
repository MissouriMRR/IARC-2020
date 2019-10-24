import unittest
import os
from vision.blob.blobfind import find_blobs

class TestBlobbing(unittest.TestCase):
    def test_finding_blobs(self):
        """
        Tests that the expected number of blobs is found

        Settings
        --------
        :var samples_directory: relative path to a directory of sample images
        :var expected_blobs: list of expected blobs to be found in each image
        :var logging: bool for whether to output details about the assertion

        Returns
        -------
        :return ndarray[bool] Whether each image in has the correct number of
        """
        samples_directory = '../blob/samples'
        expected_blobs = [1, 30, 1, 1]
        logging = False
        found_blobs = []
        vision_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        for img in os.listdir(samples_directory):
            img_file = os.path.join(vision_folder, 'blob', 'samples', img)
            keypoints = find_blobs(img_file, logging)
            found_blobs.append(len(keypoints))

        if logging:
            print("Expected:", expected_blobs)
            print("Found:", found_blobs)

        self.assertLessEqual(list(expected_blobs), list(found_blobs))


if __name__ == '__main__':
    unittest.main()
