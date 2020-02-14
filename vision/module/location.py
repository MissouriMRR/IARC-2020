"""
"""

import cv2
import numpy as np

class ModuleLocation:
    """
    Finds the distance to the front face of the module.
    """

    ## Initialization

    def __init__(self):
        self.img = np.array(0) # Color image input
        self.depth = np.array(0) # Depth image input

        self.holes = np.array(0) # Location of four holes
        
        self.circles = np.array(0) # List of circles detected in color image
        
        self.x_heights = np.array(0) # Histogram of x-coordinate values
        self.x_bounds = np.array(0) # x-coordinate bounds of histogram
        self.y_heights = np.array(0) # Histogram of y-coordinate values
        self.y_bounds = np.array(0) # y-coordinate bounds of histogram

        self.center = np.array(0) # Coordinates of center
        self.distance = 0 # Distance to the center

        self.slopes = np.array(0) # Slopes between circles
        self.slope_heights = np.array(0) # Histogram of heights

    ## Finding Distance to Module

    def getDistance(self):
        """
        Finds the distance to the module.
        Returns
        -------
        int - distance to the module.
        """
        self._getCenter()
        self.distance = self.depth[self.center[0], self.center[1], 0]
        return self.distance

    ## Finding the Center

    def _getCenter(self):
        """
        Find the center of the front face of the module.
        Returns
        -------
        ndarray - coordinates of the center of the module.
        """

        self._getHoleLocations()

        # Coordinates of the center of the front face of the module
        self.center = np.arange(0, 2)

        x_total = 0
        y_total = 0
        for x, y in self.holes:
            x_total += x
            y_total += y
        self.center[0] = x_total // 4
        self.center[1] = y_total // 4

        return self.center
    
    def _getHoleLocations(self):
        """
        Finds the locations of the 4 holes on the front face of the module.

        Returns
        -------
        ndarray - locations of the 4 holes
        """
        self._getSlopes()
        self._groupSlopes()

        self.holes = np.arange(0, 8)
        self.holes = np.reshape(self.holes, (4, 2)) # Set of 4 (x, y) coordinates

        

        return self.holes

    def _groupSlopes(self):
        """
        Bucket sort slopes to find parallels.
        Returns
        -------
        None
        """
        BUCKET_MODIFIER = 1 # Changes how many buckets are in the range

        upper_bound = np.amax(self.slopes)
        lower_bound = np.amin(self.slopes)
        num_buckets = np.int32(upper_bound - lower_bound) * BUCKET_MODIFIER

        self.slope_heights, _ = np.histogram(self.slopes, num_buckets, (lower_bound, upper_bound))

    def _getSlopes(self):
        """
        Finds slopes between detected circles
        Returns
        -------
        None
        """
        self.slopes = np.array([])
        for x, y, _ in self.circles:
            for iX, iY, _ in self.circles:
                m = (iY - y) / (iX - x)
                # slope must be non-infinite and can't be between the same circle
                if (not np.isnan(m)) and (not np.isinf(m)) and (x != iX and y != iY):
                    self.slopes = np.append(self.slopes, m)
        
        # Convert slopes to degrees
        self.slopes = np.degrees(np.arctan(self.slopes))

    def _circleDetection(self):
        """
        Returns
        -------
        ndarray - circles detected in image.
        """
        # Size of the blur kernel
        BLUR_SIZE = 5

        # Grayscale
        gray = cv2.cvtColor(src=self.img, code=cv2.COLOR_RGB2GRAY)

        # Guassian Blur
        blur = cv2.GaussianBlur(src=gray, ksize=(BLUR_SIZE,BLUR_SIZE), sigmaX=0)

        # Laplacian Transform
        laplacian = cv2.Laplacian(src=blur, ddepth=cv2.CV_8U, ksize=3)
        laplacian = np.uint8(laplacian)
        
        # Hough Circle Detection
        self.circles = cv2.HoughCircles(image=laplacian, method=cv2.HOUGH_GRADIENT, dp=1, minDist=6, param1=63, param2=30, minRadius=0, maxRadius=50)
        self.circles = np.uint16(self.circles)

        # Resize circles into 2d array
        self.circles = np.reshape(self.circles, (np.shape(self.circles)[1], 3))
        
        return self.circles

    def _increaseBrightness(self, increase):
        """
        Increases the brightness of the image.

        Returns
        -------
        None
        """
        self.img += increase

    ## Outside Input Functions

    def setImg(self, color, depth):
        """
        Sets the image detection is performed on.

        Returns
        -------
        None
        """
        self.depth = depth
        self.img = color

    ## Visualization Functions

    def showImg(self):
        """
        Shows the initial input image.

        Returns
        -------
        None
        """
        cv2.imshow("Module Location Image", self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def showCircles(self):
        """
        Shows an image of detected circles.

        Returns
        -------
        """

        circleImg = np.copy(self.img)

        for x, y, r in self.circles:
            cv2.circle(circleImg, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(circleImg, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

        cv2.imshow("Module Circles", circleImg)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    
    def showCenter(self):
        """
        Shows the image with detected holes and center.

        Returns
        -------
        None
        """
        
        centerImg = np.copy(self.img)
        for x, y in self.holes:
            cv2.circle(img=centerImg, center=(x, y), radius=10, color=(0, 0, 255), thickness=-1)
        
        cv2.circle(img=centerImg, center=(self.center[0], self.center[1]), radius=10, color=(0, 255, 0), thickness=-1)

        cv2.imshow("Module Location Center", centerImg)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
if __name__ == "__main__":
    import os

    prefix = 'vision' if os.path.isdir('vision') else ''
    filename = os.path.join(prefix, "vision_images", "module", "blocks1.jpg")
    image = cv2.imread(filename)
    if image is None:
        print(f'Failed to read image: {filename}')
        exit()
    
    loc = ModuleLocation()