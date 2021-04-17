"""
This file contains the ModuleLocation class to find the location of the center of the module in an image.
"""

import cv2
import numpy as np

from vision.text.detect_words import TextDetector
from vision.bounding_box import ObjectType, BoundingBox


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
        self.clusters = []  # list of grouped circles that are near each other
        self.best_cluster = np.array(
            []
        )  # the ideal group of circles with the most parallel slopes

        self.center = np.arange(2)  # x, y coordinates of center
        self.holes = np.zeros(
            (4, 3), dtype=np.uint16
        )  # Set of (x, y, r) coordinates, location of the holes

        self.slopes = np.array(0)  # Slopes between detected circles
        self.slope_heights = np.array(0)  # Histogram of slopes
        self.slope_bounds = np.array(0)  # Bounds of slope histogram
        self.best_slopes = np.array(
            []
        )  # Histogram w/ greatest number of parallel slopes

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
        MAX_CIRCLES = 200  # maximum number of circles that are allowed to be detected before in_frame fails
        MIN_CIRCLES = 4  # minimum number of circles needed to perform calculations
        MIN_PARALLELS = 4  # minimum number of main parallel slopes required for holes to be detected

        if self.needs_recalc:
            self._circle_detection()  # Detect circles on color image
            self._cluster_circles()  # Group circles that are near each other

            # Only perform more calculations if there are a reasonable number of circles
            if (
                np.shape(self.circles)[0] <= MAX_CIRCLES
                and np.shape(self.circles)[0] >= MIN_CIRCLES
            ):  # not too little and not too many circles found
                if self.needs_recalc:
                    max_parallels = 0
                    for cluster in self.clusters:
                        # Attempt Slopes and Parallels with current cluster
                        self._get_slopes(cluster)
                        self._group_slopes(cluster)

                        new_parallels = np.max(self.slope_heights)
                        if (
                            new_parallels > max_parallels
                            and new_parallels >= MIN_PARALLELS
                        ):
                            max_parallels = new_parallels
                            self.best_slopes = self.slope_heights
                            self.best_cluster = cluster

                        self.needs_recalc = False
            else:
                return False

        return any(self.best_slopes > MIN_SLOPES_IN_BUCKET)

    ## Finding the Center

    def get_center(self) -> tuple:
        """
        Find the center of the front face of the module.

        Returns
        -------
        tuple - (x, y) coordinates of the center of the module.
        """
        MAX_CIRCLES = 200  # slope calculations are not performed if there are more than MAX_CIRCLES circles
        MIN_CIRCLES = 4  # minimum number of circles to perform more calculations
        MIN_PARALLELS = 4  # minimum number of main parallel slopes required for holes to be detected

        if self.needs_recalc:
            self._circle_detection()  # Detect circles on color image
            self._cluster_circles()  # Group circles that are near each other

            # Only perform more calculations if there are a reasonable number of circles
            if (
                np.shape(self.circles)[0] <= MAX_CIRCLES
                and np.shape(self.circles)[0] >= MIN_CIRCLES
            ):
                max_parallels = 0
                for cluster in self.clusters:
                    # Attempt Slopes and Parallels with current cluster
                    self._get_slopes(cluster)
                    self._group_slopes(cluster)

                    new_parallels = np.max(self.slope_heights)
                    if new_parallels > max_parallels and new_parallels >= MIN_PARALLELS:
                        max_parallels = new_parallels
                        self.best_slopes = self.slope_heights
                        self.best_cluster = cluster

                    self.needs_recalc = False

            # Find the Holes
            self._get_hole_locations(self.best_cluster)

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

    def _get_hole_locations(self, circles) -> np.ndarray:
        """
        Finds the locations of the 4 holes on the front face of the module.

        Returns
        -------
        ndarray - locations of the 4 holes
        """
        NUM_CIRCLES = np.shape(circles)[0]  # The number of circles

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
                    self.holes = np.array(circles[x])
                else:
                    self.holes = np.append(self.holes, circles[x])

                self.holes = np.append(self.holes, circles[y])
                hole_idx += 1
            idx += 1

        self.holes = self.holes.reshape((-1, 3))
        self.holes = np.unique(self.holes, axis=0)  # remove duplicates
        return self.holes

    def _group_slopes(self, circles) -> None:
        """
        Bucket sort slopes to find parallels.

        Returns
        -------
        None
        """
        BUCKET_MODIFIER = 2  # Changes how many buckets are in the range
        NUM_CIRCLES = np.shape(circles)[0]  # The number of circles
        NUM_SLOPES = np.shape(self.slopes)[0]  # The number of slopes

        # Get parameters for bucket sorting
        self.upper_bound = np.amax(self.slopes)
        self.lower_bound = np.amin(self.slopes)

        interquartile_range: np.float64 = np.percentile(
            self.slopes, 75
        ) - np.percentile(self.slopes, 25)
        bucket_width: np.float64 = (2 * interquartile_range) / (
            NUM_SLOPES ** (1 / 3)
        )  # Freedman–Diaconis rule
        self.num_buckets: int = (
            int(round((self.upper_bound - self.lower_bound) / bucket_width))
            + BUCKET_MODIFIER
        )

        # Bucket sort
        self.slope_heights, self.slope_bounds = np.histogram(
            self.slopes, self.num_buckets, (self.lower_bound, self.upper_bound)
        )

    def _get_slopes(self, circles) -> None:
        """
        Finds slopes between detected circles

        Returns
        -------
        None
        """
        self.slopes = np.array([])
        for x, y, _ in circles:
            for iX, iY, _ in circles:
                m = (iY - y) / (iX - x)
                # slope must be non-infinite and can't be between the same circle
                if (not np.isnan(m)) and (not np.isinf(m)) and (x != iX and y != iY):
                    self.slopes = np.append(self.slopes, m)

        # Convert slopes to degrees
        self.slopes = np.degrees(np.arctan(self.slopes))

    ## Image Processing

    def _increase_brightness(self, offset: int) -> np.ndarray:
        """
        Increases brightness of self.img by scaling the median to 128 + an offset

        Parameters
        ----------
        offset: int
            The offset at which to scale the median brightness to. Range: [-128, 127]

        Returns
        -------
        np.ndarray - brightened color image
        """
        # Get gray scale of color image
        gray = cv2.cvtColor(src=self.img, code=cv2.COLOR_RGB2GRAY)

        # Calculate magnitude of brightness based on median + offset
        alpha_value = (128 + offset) / (np.median(gray))

        # Brighten image
        brightened_image = cv2.addWeighted(
            src1=self.img, alpha=alpha_value, src2=0, beta=0, gamma=0
        )  # brightened_image = src1*alpha + src2*beta + gamma

        return brightened_image

    def _filter_text_circles(self) -> np.ndarray:
        """
        Filters out circles that are to the left of, right of, or above text.

        Returns
        -------
        None
        """
        # Detect text
        detector = TextDetector()
        text_boxes = detector.detect_russian_word(self.img, self.depth)

        # Return if text detection fails
        if not text_boxes:
            return self.circles

        # Convert BoundingBoxes to list of values per axis
        vertices = np.array(
            [vertex for bbox in text_boxes for vertex in bbox.vertices]
        )  # unravel into list of vertices
        axes_vals = vertices.transpose()  # axis_vals[0] = x, axis_vals[1] = y

        # Find max and min values for each axis
        max_x = np.max(axes_vals[0])
        min_x = np.min(axes_vals[0])
        max_y = np.max(axes_vals[1])
        min_y = np.min(axes_vals[1])

        # Create rectangle that encompasses all detected text boxes
        # ul_bound = (min_x, min_y) # upper left corner #NOTE: not needed
        # ur_bound = (max_x, min_y) # upper right corner #NOTE: not needed
        ll_bound = (min_x, max_y)  # lower left corner
        lr_bound = (max_x, max_y)  # lower right corner

        # Filter out rectangles that are not directly below text
        circle_filter = np.array(
            [], dtype=np.uint16
        )  # array of indices of circles out of bounds

        i = 0
        for x, y, _ in self.circles:
            if y <= lr_bound[1]:  # remove if above lower bound of text
                circle_filter = np.append(circle_filter, i)
            elif (
                x <= ll_bound[0] or x >= lr_bound[0]
            ):  # remove if horizontally outside text
                circle_filter = np.append(circle_filter, i)
            i += 1

        self.circles = np.delete(self.circles, circle_filter, axis=0)

    def _filter_distant_circles(self, depth_threshold: int) -> np.ndarray:
        """
        Filters circles that are too far away based on the depth image

        Parameters
        ----------
        depth_threshold: int
            The depth distance (in millimeters) at which to consider circles too far away

        Returns
        -------
        None
        """
        # Create filter of far away circles based on depth image
        circle_filter = np.array(
            [], dtype=np.uint16
        )  # array of indices of distant circles

        i = 0
        for x, y, _ in self.circles:
            if (
                self.depth[y][x] > depth_threshold
            ):  # if too far away, remove (add index to filter)
                circle_filter = np.append(circle_filter, i)
            i += 1

        self.circles = np.delete(self.circles, circle_filter, axis=0)

    def _cluster_circles(self) -> None:
        """
        Groups circles that are near each other, and filters/removes ones that are and not near other circles

        Returns
        -------
        None
        """
        MIN_CIRCLES = 5  # minimum number of total circles to require clusting
        CLSTR_CRITERIA = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        COMPACT_THRESH = 40000  # NOTE: May need scaling up for higher res, only tested with 480p data
        MAX_CLUSTERS = 30

        if self.circles.shape[0] < 5:  # not enough circles for clustering
            return self.circles

        num_clusters = 2
        compactness = COMPACT_THRESH + 1  # init compactness to enter while loop
        while compactness > COMPACT_THRESH:  # ensure low variance within clusters
            compactness, labels, _ = cv2.kmeans(
                data=self.circles.astype(np.float32),  # kmeans requires float32
                K=num_clusters,
                bestLabels=None,
                criteria=CLSTR_CRITERIA,
                attempts=30,
                flags=cv2.KMEANS_PP_CENTERS,
            )
            if num_clusters > MAX_CLUSTERS:
                return self.circles
            if compactness > COMPACT_THRESH:
                num_clusters += 1  # try higher K value

        labels = np.ravel(labels)  # flatten column vector

        # Organize circles into a list of clusters
        self.clusters = [[] for x in np.arange(num_clusters)]
        for i in np.arange(labels.shape[0]):
            cluster_index = labels[i]
            self.clusters[cluster_index].append(list(self.circles[i]))

        self._filter_small_clusters()  # remove clusters w/ < MIN_CIRCLES circles

    def _filter_small_clusters(self) -> None:
        """
        Filters out clusters with less than 4 circles in them

        Returns
        -------
        None
        """
        MIN_CLUSTERS = 4  # minimum number of clusters to identify group as the module

        i = 0  # cluster index counter
        while i < len(self.clusters):
            if len(self.clusters[i]) < MIN_CLUSTERS:
                del self.clusters[i]
            else:
                i += 1

    def _circle_detection(self) -> np.ndarray:
        """
        Uses cv2 to detect circles in the color image.

        Returns
        -------
        ndarray - circles detected in image.
        """
        BLUR_SIZE = 5  # Size of the blur kernel
        # NOTE: Blur size may need increase w/ higher resolution, only tested on 480p data set
        BRIGHTNESS_OFFSET = 42  # offset for brightness magnitude calculation
        DEPTH_THRESH = 5000  # (in mm), tolerated dist. to filter circles

        ## Image Pre-processing ##
        # Increase brightness of image
        bright = self._increase_brightness(offset=BRIGHTNESS_OFFSET)

        # Grayscale
        bright_gray = cv2.cvtColor(src=bright, code=cv2.COLOR_RGB2GRAY)

        # Guassian Blur / Median Blur
        blur = cv2.GaussianBlur(src=bright_gray, ksize=(BLUR_SIZE, BLUR_SIZE), sigmaX=0)
        # blur = cv2.medianBlur(gray, 15)
        # blur = cv2.bilateralFilter(src=gray, d=11, sigmaColor=75, sigmaSpace=75)

        # Laplacian Transform / ksize = 3 for Guassian / ksize = 1 for Median
        laplacian = cv2.Laplacian(src=blur, ddepth=cv2.CV_8U, ksize=3)
        laplacian = np.uint8(laplacian)

        ## Hough Circle Detection ##
        self.circles = cv2.HoughCircles(  # NOTE: Params may need partial rework, only tested on 480p data
            image=laplacian,
            method=cv2.HOUGH_GRADIENT,
            dp=1,
            minDist=10,
            param1=70,  # canny edge detector gradient upper threshold
            param2=14,  # accumulator threshold for circle centers
            minRadius=0,
            maxRadius=10,  # NOTE: May need to be increased, only tested on 480p data
        )

        ## Reformatting ##
        # Prevents TypeError if no circles detected
        if self.circles is None:
            self.circles = np.array([])
            return self.circles

        self.circles = np.uint16(self.circles)

        # Resize circles into 2d array
        self.circles = np.reshape(self.circles, (np.shape(self.circles)[1], 3))

        ## Post-Processing: Circle filtering and grouping ##
        # Remove circles that aren't directly below text
        self._filter_text_circles()

        # Remove circles that are farther than DEPTH_THRESHOLD millimeters away
        self._filter_distant_circles(DEPTH_THRESH)

        return self.circles

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
        # Set depth and color images
        self.depth = depth
        self.img = color

        # Re-initialize all important values to zero/empty
        self.circles = np.array([])
        self.clusters = []
        self.best_cluster = np.array([])

        self.best_slopes = np.array([])

        self.center = np.arange(2)
        self.holes = np.zeros((4, 3), dtype=np.uint16)

        self.needs_recalc = True

    ## Visualization Functions

    def show_img(self, draw_circles: bool = False, draw_center: bool = False) -> None:
        """
        Displays color image, with color-coded circles and/or center if desired.

        Circle color-coding:
        -   White & filled in: The best_cluster of circles used for center & in_frame calculation
        -   Green w/ orange center square: Circles in clusters that have less than 4 circles
        -   Other colors: Unused clusters that didn't have as many parallel slopes as best_cluster

        Parameters
        ----------
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
            # draw all circles
            for x, y, r in self.circles:
                cv2.circle(circle_img, (x, y), r, (0, 255, 0), 1)  # green outer circle
                cv2.rectangle(
                    circle_img, (x - 1, y - 1), (x + 1, y + 1), (0, 128, 255), 1
                )  # center orange rectangle

            # draw clusters over self.circles
            for cluster in self.clusters:
                color = np.random.choice(range(256), size=3)
                color = (int(color[0]), int(color[1]), int(color[2]))
                thickness = 1
                if (
                    cluster == self.best_cluster
                ):  # make the best_cluster white and filled in
                    color = (255, 255, 255)
                    thickness = -1
                for x, y, r in cluster:
                    cv2.circle(
                        img=circle_img,
                        center=(x, y),
                        radius=r,
                        color=color,
                        thickness=thickness,
                    )
                    cv2.rectangle(
                        img=circle_img,
                        pt1=(x - 1, y - 1),
                        pt2=(x + 1, y + 1),
                        color=color,
                        thickness=-1,
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

        draw_circ_title = " w/ Clustered Hough Circles" if draw_circles else ""
        draw_cent_title = " w/ Module Center" if draw_center else ""

        cv2.imshow(
            "Module Location Image" + draw_circ_title + draw_cent_title, circle_img
        )
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def show_depth(self) -> None:
        """
        Shows the depth channel image.

        Returns
        -------
        None
        """
        cv2.imshow(
            "Module Depth Image", np.uint8((self.depth / np.amax(self.depth)) * 255)
        )
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def save_img(
        self, file: str, draw_circles: bool = False, draw_center: bool = False
    ) -> None:
        """
        Saves image, with color-coded circles and/or center if desired, to file.

        Circle color-coding:
        -   White & filled in: The best_cluster of circles used for center & in_frame calculation
        -   Green w/ orange center square: Circles in clusters that have less than 4 circles
        -   Other colors: Unused clusters that didn't have as many parallel slopes as best_cluster

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
            # draw all circles
            for x, y, r in self.circles:
                cv2.circle(circle_img, (x, y), r, (0, 255, 0), 1)  # green outer circle
                cv2.rectangle(
                    circle_img, (x - 1, y - 1), (x + 1, y + 1), (0, 128, 255), 1
                )  # center orange rectangle

            # draw clusters over self.circles
            for cluster in self.clusters:
                color = np.random.choice(range(256), size=3)
                color = (int(color[0]), int(color[1]), int(color[2]))
                thickness = 1
                if (
                    cluster == self.best_cluster
                ):  # make the best_cluster white and filled in
                    color = (255, 255, 255)
                    thickness = -1
                for x, y, r in cluster:
                    cv2.circle(
                        img=circle_img,
                        center=(x, y),
                        radius=r,
                        color=color,
                        thickness=thickness,
                    )
                    cv2.rectangle(
                        img=circle_img,
                        pt1=(x - 1, y - 1),
                        pt2=(x + 1, y + 1),
                        color=color,
                        thickness=-1,
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
