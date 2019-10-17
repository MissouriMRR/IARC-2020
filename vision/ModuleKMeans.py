import numpy as np
import cv2

class ModuleKMeans:

    """
    Applies the kmeans algorithm to an image and displays a remapped
    version of the image showing either the remapped colors or a black
    and white image showing only specified color channels

    Paramters
    ---------
    imgPath: string
        Reads in the image with this name to be used
    """
    def __init__(self, imgPath):
        self.img = cv2.imread(imgPath)
        self.Z = self.img.reshape((-1, 3))
        self.Z = np.float32(self.Z)


    """
    Applies the kmeans algorithm to the image

    Parameters
    ----------
    K: int
        Number of centers to use for the kmeans algorithm
        (bigger K = more variety of colors)
    """
    def applyKMeans(self, K):
        self.criteria = (cv2.TERM_CRITERIA_EPS +
                         cv2.TERM_CRITERIA_MAX_ITER,
                         10, 1.0)
        self.ret,self.label,self.center = cv2.kmeans(self.Z, K, None,
                                                     self.criteria, 10,
                                                     cv2.KMEANS_RANDOM_CENTERS)


    """
    Displays the remapped image with simplified colors
    """
    def displayFractal(self):
        self.center = np.uint8(self.center)
        self.res = self.center[self.label.flatten()]
        self.res2 = self.res.reshape((self.img.shape))

        cv2.imshow('res2', self.res2)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


    """
    Displays the image with only specified channels being white

    Parameters
    ----------
    channels: list of ints
        Channels specified in this parameter will be white while all
        others will be black
    """
    def displayBinary(self, channels):
        self.white = [255, 255, 255]
        self.black = [0, 0, 0]

        for i in self.label.reshape(self.img.shape[:2]):
            self.img[self.label.reshape(self.img.shape[:2]) == i] = np.array(self.black)

        for i in channels:
            self.img[self.label.reshape(self.img.shape[:2]) == i] = np.array(self.white)

        cv2.imshow('img', self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
