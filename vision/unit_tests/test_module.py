"""
For testing all module algorithms.
"""
import os, sys
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path += [parent_dir]
sys.path += [os.path.dirname(parent_dir)]

import unittest
import cv2

from vision.module.in_frame import ModuleInFrame as mif
from vision.module.detector import ModuleKMeans as mkm


class TestModuleInFrame(unittest.TestCase):
    def test_ModuleInFrame(self):
        """
        Testing ModuleInFrame
        
        Returns
        -------
        ndarray[bool] which images the module was detected in
        """

        results = []
        expected_results = {
            "Block1.jpg" : True,
            "Block2.jpg" : True,
            "Block3.jpg" : True,
            "Block4.jpg" : True
        }
        print(os.getcwd())
        for picname in expected_results.keys():
<<<<<<< HEAD:vision/unit_tests/test_modulecheck.py
            picpath = os.path.join('vision', 'vision_images', 'module', picname)
            results.append(mif(cv2.imread(picpath)))

=======
            picpath = os.path.join('vision_images', 'module', picname)
            
            image = cv2.imread(picpath)

            if image is None:
                raise FileNotFoundError(f"Could not read {picpath}!")

            results.append(mif(image))
       
>>>>>>> 6b1016a256fd45ffcef4478de024fe3c93b91263:vision/unit_tests/test_module.py
        self.assertListEqual(results, list(expected_results.values()))


class TestKMeans(unittest.TestCase):
    pass


if __name__ == '__main__':
        unittest.main()
