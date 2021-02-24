"""
This file contains the ModuleLocation class to find the location of the center of the module in an image.
"""

import os
import cv2
import numpy as np


class ModuleLocation:
    """
    Finds the coordinates of the center of the front face of the module.
    """

    ## Initialization

    def __init__(self):
        np.seterr(all="ignore")  # Ignore numpy warnings

        self.img = np.array(0)  # Color image input
        self.depth = np.array(0)  # Depth image input

        self.circles = np.array(0)  # Array of circles detected in color image

        self.center = np.arange(2)  # x, y coordinates of center
        self.holes = np.zeros(
            (4, 3)
        )  # Set of (x, y, r) coordinates, location of the holes

        self.slopes = np.array(0)  # Slopes between detected circles
        self.slope_heights = np.array(0)  # Histogram of slopes
        self.slope_bounds = np.array(0)  # Bounds of slope histogram

        self.upper_bound = np.array(0)  # upper bound of slopes
        self.lower_bound = np.array(0)  # lower bound of slopes
        self.num_buckets = np.array(0)  # number of buckets applied to slopes

        self.needsRecalc = (
            True  # Prevents recalculation of circles, slopes, and slope grouping
        )

    ## Determining if Module is in frame

    def isInFrame(self) -> bool:
        """
        Determines if the Module is in the frame

        Returns
        -------
        bool - true if module is in the frame and false if module is not in the frame
        """
        MIN_SLOPES_IN_BUCKET = (
            15  # Minimum number of slopes per bucket to identify the module
        )
        MAX_CIRCLES = 100  # maximum number of circles that are allowed to be detected before in_frame fails
        MIN_CIRCLES = 4  # minimum number of circles needed to perform calculations

        if self.needsRecalc:
            # Circle Detection
            self._circleDetection()

        if (
            np.shape(self.circles)[0] < MIN_CIRCLES
            or np.shape(self.circles)[0] > MAX_CIRCLES
        ):  # too little or too many circles found
            return False

        if self.needsRecalc:
            # Get slopes and group parallel slopes
            self._getSlopes()
            self._groupSlopes()
            self.needsRecalc = False

        return any(self.slope_heights > MIN_SLOPES_IN_BUCKET)

    ## Finding the Center

    def getCenter(self) -> tuple:
        """
        Find the center of the front face of the module.

        Returns
        -------
        tuple - (x, y) coordinates of the center of the module.
        """
        MAX_CIRCLES = 100  # slope calculations are not performed if there are more than MAX_CIRCLES circles
        MIN_CIRCLES = 4  # minimum number of circles to perform more calculations

        if self.needsRecalc:
            # Circle detection
            self._circleDetection()

        # Filter out far away circles
        # self._filterCircleDepth()

        # Only perform more calculations if there are few circles
        if (
            np.shape(self.circles)[0] <= MAX_CIRCLES
            and np.shape(self.circles)[0] > MIN_CIRCLES
        ):
            if self.needsRecalc:
                # Get Slopes and Parallels
                self._getSlopes()
                self._groupSlopes()
                self.needsRecalc = False

            # Find the Holes
            self._getHoleLocations()

            # Coordinates of the center of the front face of the module
            self.center = np.arange(0, 2)

            # Average hole coordinates to find center coordinates
            x_total = 0
            y_total = 0
            num_holes = 0
            for x, y, _ in self.holes:
                x_total += x
                y_total += y
                num_holes += 1

            self.center[0] = x_total // num_holes
            self.center[1] = y_total // num_holes

        # Returns either the center in the current image
        # or the previous center if no slope calculations were performed
        return tuple(self.center)

    def _filterCircleDepth(self) -> np.ndarray:
        """
        Filters out circles based on the depth at the circles' centers.

        Returns
        -------
        ndarray - circles with depth at center.
        """
        DEPTH_THRESH = 1000

        nCir = np.array([0, 0, 0])  # new array of circles within DEPTH_THRESH
        count = 0

        for x, y, r in self.circles:
            if (
                x < np.shape(self.img)[0] and y < np.shape(self.img)[1]
            ):  # eliminate circles outside of the image
                if (
                    self.depth[x, y] < DEPTH_THRESH and self.depth[x, y] != 0
                ):  # remove far-away circles
                    if count == 0:
                        nCir = np.array([x, y, r])
                    else:
                        nCir = np.append(nCir, [x, y, r])
                    count += 1

        if np.shape(nCir)[0] != 0:
            nCir = nCir.reshape((-1, 3))
            self.circles = nCir

    def _getHoleLocations(self) -> np.ndarray:
        """
        Finds the locations of the 4 holes on the front face of the module.

        Returns
        -------
        ndarray - locations of the 4 holes
        """
        NUM_CIRCLES = np.shape(self.circles)[0]  # The number of circles

        sep = (self.upper_bound - self.lower_bound) / (
            self.num_buckets
        )  # seperation from main parallel, width of a bucket

        # Find Slope with Most Parallels
        bucket_ind = np.argmax(self.slope_heights)  # highest segment of histogram
        parallel = self.slope_bounds[bucket_ind] - (
            sep / 2
        )  # slope at highest segment minus half bucket width is main parallel

        # Find Holes Associated with parallels
        idx = 0
        hole_idx = 0
        for slope in self.slopes:
            if np.abs(slope - parallel) <= sep:
                # x and y are the indexes of 2 circles corresponding to a slope
                x = idx // (NUM_CIRCLES - 1)
                y = idx % (NUM_CIRCLES - 1)
                y += int(y >= x)

                if hole_idx == 0:
                    self.holes = np.array(self.circles[x])
                else:
                    self.holes = np.append(self.holes, self.circles[x])

                self.holes = np.append(self.holes, self.circles[y])
                hole_idx += 1
            idx += 1

        self.holes = self.holes.reshape((-1, 3))
        return self.holes

    def _groupSlopes(self) -> None:
        """
        Bucket sort slopes to find parallels.

        Returns
        -------
        None
        """
        BUCKET_MODIFIER = 0.5  # Changes how many buckets are in the range

        # Get parameters for bucket sorting
        self.upper_bound = np.amax(self.slopes)
        self.lower_bound = np.amin(self.slopes)
        self.num_buckets = np.int32(
            (self.upper_bound - self.lower_bound) * BUCKET_MODIFIER
        )

        # Bucket sort
        self.slope_heights, self.slope_bounds = np.histogram(
            self.slopes, self.num_buckets, (self.lower_bound, self.upper_bound)
        )

    def _getSlopes(self) -> None:
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

    def _circleDetection(self) -> np.ndarray:
        """
        Uses cv2 to detect circles in the color image.

        Returns
        -------
        ndarray - circles detected in image.
        """
        # Size of the blur kernel
        BLUR_SIZE = 5

        # Grayscale
        gray = cv2.cvtColor(src=self.img, code=cv2.COLOR_RGB2GRAY)

        # Guassian Blur / Median Blur
        # blur = cv2.GaussianBlur(src=gray, ksize=(BLUR_SIZE, BLUR_SIZE), sigmaX=0)
        blur = cv2.medianBlur(gray, 13)

        # Laplacian Transform / ksize = 3 for Guassian
        laplacian = cv2.Laplacian(src=blur, ddepth=cv2.CV_8U, ksize=1)
        laplacian = np.uint8(laplacian)

        # Hough Circle Detection
        self.circles = cv2.HoughCircles(
            image=laplacian,
            method=cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=8,
            param1=75,
            param2=24,
            minRadius=0,
            maxRadius=50,
        )

        # Prevents TypeError if no circles detected
        if self.circles is None:
            self.circles = np.array([])
            return self.circles

        self.circles = np.uint16(self.circles)

        # Resize circles into 2d array
        self.circles = np.reshape(self.circles, (np.shape(self.circles)[1], 3))

        return self.circles

    ## Image Processing

    def _filterDepth(self) -> None:
        """
        Uses the depth channel to eliminate far away parts of the color image

        Returns
        -------
        None

        Note: not in use
        """
        DEPTH_THRESH = 200  # Values from depth image that are "zeroed" in color image

        tempDepth = np.dstack((self.depth, self.depth, self.depth))
        self.img = np.where(tempDepth < DEPTH_THRESH, self.img, 0)

    def _increaseBrightness(self, increase: int) -> None:
        """
        Increases the brightness of the image.

        Parameters
        ----------
        increase: int
            The increase in brightness of RGB values.

        Returns
        -------
        None

        Note: not in use
        """
        self.img += increase

    ## Input Functions

    def setImg(self, color: np.ndarray, depth: np.ndarray) -> None:
        """
        Sets the image detection is performed on.

        Parameters
        ----------
        color: ndarray
            The color image.
        depth: ndarray
            The depth image.

        Returns
        -------
        None
        """
        self.depth = depth
        self.img = color
        self.needsRecalc = True

    ## Visualization Functions

    def showImg(self) -> None:
        """
        Shows the initial input image.

        Returns
        -------
        None
        """
        cv2.imshow("Module Location Image", self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def showDepth(self) -> None:
        """
        Shows the depth channel image.

        Returns
        -------
        None
        """
        cv2.imshow("Module Depth Image", self.depth)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def showCircles(self) -> None:
        """
        Shows an image of detected circles.

        Returns
        -------
        None
        """

        circleImg = np.copy(self.img)

        for x, y, r in self.circles:
            cv2.circle(circleImg, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(circleImg, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

        cv2.imshow("Module Circles", circleImg)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def saveCircleImage(self, filename) -> None:
        """
        Saves image with circles in folder Circle_Images.

        Returns
        -------
        None
        """

        circleImg = np.copy(self.img)

        for x, y, r in self.circles:
            cv2.circle(circleImg, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(circleImg, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

        OUTPUT_FILE = "Circle_Images"
        try:
            os.mkdir(OUTPUT_FILE)
        except FileExistsError:
            pass

        cv2.imwrite(os.path.join(OUTPUT_FILE, filename), circleImg)

    def showCenter(self) -> None:
        """
        Shows the image with detected holes and center.

        Returns
        -------
        None
        """

        centerImg = np.copy(self.img)
        for x, y, r in self.holes:
            cv2.circle(
                img=centerImg,
                center=(int(x), int(y)),
                radius=int(r),
                color=(0, 0, 255),
                thickness=-1,
            )

        cv2.circle(
            img=centerImg,
            center=(self.center[0], self.center[1]),
            radius=10,
            color=(0, 255, 0),
            thickness=-1,
        )

        cv2.imshow("Module Location Center", centerImg)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    import os

    prefix = "vision" if os.path.isdir("vision") else ""
    filename = os.path.join(
        prefix,
        "vision_images",
        "module",
        "Feb29",
        "2020-02-29_15.36.15.079345-colorImage.jpg",
    )
    depthname = os.path.join(
        prefix,
        "vision_images",
        "module",
        "Feb29",
        "2020-02-29_15.36.15.079345-depthImage.npy",
    )
    image = cv2.imread(filename)
    depth = np.load(depthname)

    if image is None:
        print(f"Failed to read image: {filename}")
        exit()
    if depth is None:
        print(f"Failed to load depth image: {depthname}")
        exit()

    loc = ModuleLocation()

    loc.setImg(image, depth)

    print(loc.getCenter())
    print(loc.getDistance())

    loc.showCenter()
