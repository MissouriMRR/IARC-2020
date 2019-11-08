import unittest
import os
import sys
import cv2

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

from vision.blob.blobfind import BlobFinder


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
        expected_blobs = {
            "apple.jpg": 1,
            "legos.jpg": 30,
            "MyBeach.png": 1,
            "oranges.png": 1,
            "sampleobj.png": 1
        }
        if os.path.isdir("vision"):
            prefix = os.path.join('vision', 'blob')
        elif os.path.isdir('blob'):
            prefix = 'blob'
        else:
            prefix = ''

        for i, img in enumerate(os.listdir(os.path.join(prefix, 'samples'))):
            with self.subTest(i=img):
                img_file = os.path.join(prefix, 'samples', img)
                img_file = cv2.imread(img_file)
                detector = BlobFinder(img_file)
                bounding_boxes = detector.find()
                self.assertEqual(len(bounding_boxes), expected_blobs[img], msg=f"Expected {expected_blobs[img]} blobs, found {len(bounding_boxes)} in image {img}")

if __name__ == '__main__':
    unittest.main()
