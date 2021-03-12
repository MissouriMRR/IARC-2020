"""
This file contains the ModuleLocation class to find the location of the center of the module in an image.
"""

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

        self.needs_recalc = (
            True  # Prevents recalculation of circles, slopes, and slope grouping
        )

    ## Determining if Module is in frame

    def is_in_frame(self) -> bool:
        """
        Determines if the Module is in the frame

        Returns
        -------
        bool - true if module is in the frame and false if module is not in the frame
        """
        MIN_SLOPES_IN_BUCKET = (
            4  # Minimum number of slopes per bucket to identify the module
        )
        MAX_CIRCLES = 100  # maximum number of circles that are allowed to be detected before in_frame fails
        MIN_CIRCLES = 4  # minimum number of circles needed to perform calculations

        if self.needs_recalc:
            # Circle Detection
            self._circle_detection()

        # Only perform more calculations if there are a reasonable number of circles
        if (
            np.shape(self.circles)[0] <= MAX_CIRCLES
            and np.shape(self.circles)[0] >= MIN_CIRCLES
        ):  # not too little and not too many circles found
            if self.needs_recalc:
                # Get slopes and group parallel slopes
                self._get_slopes()
                self._group_slopes()
                self.needs_recalc = False
        else:
            return False

        return any(self.slope_heights > MIN_SLOPES_IN_BUCKET)

    ## Finding the Center

    def get_center(self) -> tuple:
        """
        Find the center of the front face of the module.

        Returns
        -------
        tuple - (x, y) coordinates of the center of the module.
        """
        MAX_CIRCLES = 100  # slope calculations are not performed if there are more than MAX_CIRCLES circles
        MIN_CIRCLES = 4  # minimum number of circles to perform more calculations

        if self.needs_recalc:
            # Circle detection
            self._circle_detection()

        # Filter out far away circles
        # self._filter_circle_depth()

        # Only perform more calculations if there are a reasonable number of circles
        if (
            np.shape(self.circles)[0] <= MAX_CIRCLES
            and np.shape(self.circles)[0] >= MIN_CIRCLES
        ):
            if self.needs_recalc:
                # Get Slopes and Parallels
                self._get_slopes()
                self._group_slopes()
                self.needs_recalc = False

            # Find the Holes
            self._get_hole_locations()

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

    def _filter_circle_depth(self) -> np.ndarray:
        """
        Filters out circles based on the depth at the circles' centers.

        Returns
        -------
        ndarray - circles with depth at center.
        """
        DEPTH_THRESH = 1000

        new_cir = np.array([0, 0, 0])  # new array of circles within DEPTH_THRESH
        count = 0

        for x, y, r in self.circles:
            if (
                x < np.shape(self.img)[0] and y < np.shape(self.img)[1]
            ):  # eliminate circles outside of the image
                if (
                    self.depth[x, y] < DEPTH_THRESH and self.depth[x, y] != 0
                ):  # remove far-away circles
                    if count == 0:
                        new_cir = np.array([x, y, r])
                    else:
                        new_cir = np.append(new_cir, [x, y, r])
                    count += 1

        if np.shape(new_cir)[0] != 0:
            new_cir = new_cir.reshape((-1, 3))
            self.circles = new_cir

    def _get_hole_locations(self) -> np.ndarray:
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
        self.holes = np.unique(self.holes, axis=0)  # remove duplicates
        return self.holes

    def _group_slopes(self) -> None:
        """
        Bucket sort slopes to find parallels.

        Returns
        -------
        None
        """
        BUCKET_MODIFIER = 0.5  # Changes how many buckets are in the range
        NUM_CIRCLES = np.shape(self.circles)[0]  # The number of circles
        NUM_SLOPES = np.shape(self.slopes)[0]  # The number of slopes

        # Get parameters for bucket sorting
        self.upper_bound = np.amax(self.slopes)
        self.lower_bound = np.amin(self.slopes)

        interquartile_range: np.float64 = np.percentile(self.slopes, 75) - np.percentile(
            self.slopes, 25
        )
        bucket_width: np.float64 = (2 * interquartile_range) / (
            NUM_SLOPES ** (1 / 3)
        )  # Freedman–Diaconis rule
        self.num_buckets: int = int(
            round((self.upper_bound - self.lower_bound) / bucket_width)
        )

        # Bucket sort
        self.slope_heights, self.slope_bounds = np.histogram(
            self.slopes, self.num_buckets, (self.lower_bound, self.upper_bound)
        )

    def _get_slopes(self) -> None:
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

    def _circle_detection(self) -> np.ndarray:
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
        blur = cv2.medianBlur(gray, 15)

        # Laplacian Transform / ksize = 3 for Guassian / ksize = 1 for Median
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
        Uses the depth channel to eliminate far away parts of the color image. Sets far away parts of color image to 0.

        Returns
        -------
        None

        Note: not in use
        """
        DEPTH_THRESH = 200  # Values from depth image that are "zeroed" in color image

        tempDepth = np.dstack((self.depth, self.depth, self.depth))
        self.img = np.where(tempDepth < DEPTH_THRESH, self.img, 0)

    def _increase_brightness(self, increase: int) -> None:
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

    def set_img(self, color: np.ndarray, depth: np.ndarray) -> None:
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
        self.circles = np.array([])
        self.center = np.arange(2)
        self.needs_recalc = True

    ## Visualization Functions

    def show_img(self) -> None:
        """
        Shows the initial input image.

        Returns
        -------
        None
        """
        cv2.imshow("Module Location Image", self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def show_depth(self) -> None:
        """
        Shows the depth channel image.

        Returns
        -------
        None
        """
        cv2.imshow("Module Depth Image", np.uint8((self.depth / np.amax(self.depth)) * 255))
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def show_circles(self) -> None:
        """
        Shows an image of detected circles.

        Returns
        -------
        None
        """

        circle_img = np.copy(self.img)

        for x, y, r in self.circles:
            cv2.circle(circle_img, (x, y), r, (0, 255, 0), 4)
            cv2.rectangle(circle_img, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1)

        cv2.imshow("Module Circles", circle_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def save_img(
        self, file: str, draw_circles: bool = False, draw_center: bool = False
    ) -> None:
        """
        Saves image, with circles or center if desired, in folder circles.

        Parameters
        ----------
        file: string
            Path and filename.
        draw_circles: bool
            Whether to draw detected circles on the image.
        draw_center: bool
            Whether to draw the calculated center on the image.

        Returns
        -------
        None
        """
        circle_img = np.copy(self.img)

        if draw_circles:
            for x, y, r in self.circles:
                cv2.circle(circle_img, (x, y), r, (0, 255, 0), 4)
                cv2.rectangle(
                    circle_img, (x - 5, y - 5), (x + 5, y + 5), (0, 128, 255), -1
                )

        if draw_center:
            cv2.circle(
                img=circle_img,
                center=(self.center[0], self.center[1]),
                radius=20,
                color=(0, 0, 255),
                thickness=3,
            )  # outer circle
            cv2.circle(
                img=circle_img,
                center=(self.center[0], self.center[1]),
                radius=1,
                color=(0, 0, 255),
                thickness=2,
            )  # center dot

        cv2.imwrite(file, circle_img)

    def show_center(self) -> None:
        """
        Shows the image with detected holes and center.

        Returns
        -------
        None
        """

        center_img = np.copy(self.img)
        for x, y, r in self.holes:
            cv2.circle(
                img=center_img,
                center=(int(x), int(y)),
                radius=int(r),
                color=(0, 0, 255),
                thickness=-1,
            )

        cv2.circle(
            img=center_img,
            center=(self.center[0], self.center[1]),
            radius=10,
            color=(0, 255, 0),
            thickness=-1,
        )

        cv2.imshow("Module Location Center", center_img)
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

    loc.set_img(image, depth)

    print(loc.get_center())
    print(loc.getDistance())

    loc.show_center()
