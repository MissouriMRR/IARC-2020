"""
"""

import cv2
import numpy as np

class ModuleLocation:
    """
    """

    def __init__(self):
        self.img = np.array(0)
        self.holes = np.array(0)

    def getLocation(self, img):
        """
        """
        self.img = img
        self.holes = self.getHoleLocations()
        return self.getCenter()

    def getHoleLocations(self):
        """
        Finds the locations of the 4 holes on the front face of the module.

        Returns
        -------
        ndarray - locations of the 4 holes
        """
        
    
    def getCenter(self):
        """
        Finds the location of the center of the front face of the module.
        """
        