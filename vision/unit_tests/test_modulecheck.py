"""
This file is used for testing ModuleInFrame
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
import unittest
import cv2
from vision.module_in_frame.ModuleInFrame import ModuleInFrame as mif

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
            picpath = os.path.join('vision', 'vision_images', 'module', picname)
            results.append(mif(cv2.imread(picpath)))
       
        self.assertListEqual(results, list(expected_results.values()))

if __name__ == '__main__':
        unittest.main()