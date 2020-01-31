"""
"""

import cv2
import numpy as np

class ModuleLocation:
    """
    Finds the center of the front face of the module.
    """

    def __init__(self):
        self.img = np.array(0)
        
        self.holes = np.array(0)
        
        self.circles = np.array(0)
        
        self.x_buckets = np.array(0)
        self.y_buckets = np.array(0)

    def getCenter(self, img):
        """
        Find the center of the front face of the module.
        Returns
        -------
        Tuple - coordinates of the center of the module.
        """
        self.img = img
        self.holes = self.getHoleLocations()


    def _circleDetection(self, img=self.img):
        """
        Returns
        -------
        ndarray - circles detected in image.
        """
        # Grayscale
        gray = cv2.cvtColor(src=self.img, code=cv2.COLOR_RGB2GRAY)

        # Guassian Blur
        blur = cv2.GaussianBlur(src=gray, ksize=(BLUR_SIZE,BLUR_SIZE), sigmaX=0)

        # Laplacian Transform
        laplacian = cv2.Laplacian(src=blur, ddepth=cv2.CV_8U, ksize=3)
        laplacian = np.uint8(laplacian)
        
        # Hough Circle Detection
        self.circles = cv2.HoughCircles(image=laplacian, method=cv2.HOUGH_GRADIENT, dp=1, minDist=8, param1=50, param2=40, minRadius=0, maxRadius=50)
        self.circles = np.uint16(circles)

        # Resize circles into 2d array
        self.circles = np.reshape(circles, (np.shape(circles)[1], 3))
        return circles

    def _getBuckets(self):
        """
        Bucket sorts circles in order to find holes in module.

        Returns
        -------
        ndarray - buckets of circles after detection.
        """

        self._circleDetection()

        BUCKET_MODIFIER = 1 # Changes how many buckets are in the range

        # Seperate the axis
        x_vals = np.take(self.circles, [0], 1)
        y_vals = np.take(self.circles, [1], 1)

        # Bucket sorting x values
        upper_bound = np.amax(x_vals)
        lower_bound = np.amin(x_vals)
        num_buckets = np.int32(upper_bound - lower_bound) * BUCKET_MODIFIER
        self.x_buckets, _ = np.histogram(x_vals, num_buckets, (lower_bound, upper_bound))

        # Bucket sorting y values
        upper_bound = np.amax(x_vals)
        lower_bound = np.amin(x_vals)
        num_buckets = np.int32(upper_bound - lower_bound) * BUCKET_MODIFIER
        self.y_buckets, _ = np.histogram(y_vals, num_buckets, (lower_bound, upper_bound))

    def getHoleLocations(self, img=self.img):
        """
        Finds the locations of the 4 holes on the front face of the module.

        Returns
        -------
        ndarray - locations of the 4 holes
        """
        
        
if __name__ == "__main__":
    import os

    prefix = 'vision' if os.path.isdir('vision') else ''
    filename = os.path.join(prefix, "vision_images", "module", "blocks1.jpg")
    image = cv2.imread(filename)
    if image is None:
        print(f'Failed to read image: {filename}')
        exit()
    
    loc = ModuleLocation()