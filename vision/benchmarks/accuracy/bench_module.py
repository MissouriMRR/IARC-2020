"""
For testing all module algorithms.
"""
import os, sys

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import cv2

from vision.module.in_frame import ModuleInFrame as mif
#from vision.module.detector import ModuleKMeans as mkm


class AccuracyModuleInFrame:
    """
    Testing module.in_frame accuracy.
    """
    def accuracy_ModuleInFrame(self):
        """
        Measuring accuracy of ModuleInFrame

        Returns
        -------
        bool Whether the module is in frame or not.
        """

        results = []
        expected_results = {
            "Block1.jpg" : True,
            "Block2.jpg" : True,
            "Block3.jpg" : True,
            "Block4.jpg" : True
        }
        for picname in expected_results.keys():
            with self.subTest(i=picname):
                picpath = os.path.join('vision_images', 'module', picname)

                image = cv2.imread(picpath)


                if image is None:
                    raise FileNotFoundError(f"Could not read {picpath}!")

                results.append(mif(image))

        self.assertListEqual(results, list(expected_results.values()))
