"""
This file is used for testing ModuleInFrame
"""
import os, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))) 
import unittest
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
        expected_results = [True, True, True, True]
        for pic in ["Block1.png", "Block2.png", "Block3.jpg", "Block4.jpg"]:
            results.append(mif(pic))
        self.assertListEqual(results, expected_results)
        return results

if __name__ == '__main__':
        unittest.main()