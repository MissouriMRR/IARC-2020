"""
This file contains the ModuleLocation class to find the location of the center of the module in an image.
"""

import cv2
import numpy as np

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

        self.text_boxes = []  # list of BoundingBoxes of the text in the image

        self.circles = np.array(0)  # Array of circles detected in color image
        self.clusters = []  # list of grouped circles that are near each other
        self.best_cluster = np.array(
            []
        )  # the ideal group of circles with the most parallel slopes

        self.center = np.arange(2)  # x, y coordinates of center
        self.holes = np.zeros(
            (4, 3), dtype=np.uint16
        )  # Set of (x, y, r) coordinates, location of the holes

        self.best_slopes = np.array(
            0
        )  # Slopes between detected circles of the identified module
        self.best_grouped_slopes = ()  # Histogram & bucket width of group of slopes that are most likely the modules'

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

        if self.needs_recalc:
            self._circle_detection()  # Detect circles on color image
            self._cluster_circles()  # Group circles that are near each other

            # Only perform more calculations if there are a reasonable number of circles
            if (
                np.shape(self.circles)[0] <= MAX_CIRCLES
                and np.shape(self.circles)[0] >= MIN_CIRCLES
            ):  # not too little and not too many circles found
                self.best_cluster = self._find_best_cluster()
                self.needs_recalc = False
            else:
                return False

        best_slope_heights = self.best_grouped_slopes[0]

        return np.any(best_slope_heights > MIN_SLOPES_IN_BUCKET)

    ## Finding the Center

    def get_center(self) -> tuple:
        """
        Find the center of the front face of the module.
        Returns (0, 1) if no center was found.

        Returns
        -------
        tuple - (x, y) coordinates of the center of the module.
        """
        MAX_CIRCLES = 200  # slope calculations are not performed if there are more than MAX_CIRCLES circles
        MIN_CIRCLES = 4  # minimum number of circles to perform more calculations

        if self.needs_recalc:
            self._circle_detection()  # Detect circles on color image
            self._cluster_circles()  # Group circles that are near each other

            # Only perform more calculations if there are a reasonable number of circles
            if (
                np.shape(self.circles)[0] <= MAX_CIRCLES
                and np.shape(self.circles)[0] >= MIN_CIRCLES
            ):  # not too little and not too many circles found
                self.best_cluster = self._find_best_cluster()
                self.needs_recalc = False
            else:
                return tuple(self.center)  # returns, no center found

        # Find the Holes
        self._get_hole_locations()

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
        # or the center (0, 1) if no center was found
        return tuple(self.center)

    def _find_best_cluster(self) -> np.ndarray:
        """
        Finds the cluster with the greatest amount of parallel slopes

        Returns
        -------
        np.ndarray - the group of circles with the most parallel slopes
        """
        MIN_PARALLELS = 4  # minimum number of main parallel slopes required for holes to be detected

        best_cluster = np.array([])

        max_parallels = 0
        for cluster in self.clusters:
            # Attempt Slopes and Parallels with current cluster
            slopes = self._get_slopes(cluster)  # slopes between circles
            grouped_slopes = self._group_slopes(slopes)  # bucket sorted slopes
            slope_heights = grouped_slopes[0]  # slope histogram heights

            # If this cluster returned more main parallel slopes, make it the new best_cluster
            new_parallels = np.max(slope_heights)  # just-calculated main parallels
            if new_parallels > max_parallels and new_parallels >= MIN_PARALLELS:
                max_parallels = new_parallels
                self.best_slopes = slopes
                self.best_grouped_slopes = grouped_slopes
                best_cluster = np.array(cluster)

        return best_cluster

    def _get_hole_locations(self) -> np.ndarray:
        """
        Finds the locations of the 4 holes on the front face of the module
        based on best_cluster, best_slopes, and best_grouped_slopes

        Returns
        -------
        ndarray - locations of the 4 holes
        """
        SLOPE_HEIGHTS = self.best_grouped_slopes[0]  # best histogram slope heights
        SLOPE_BOUNDS = self.best_grouped_slopes[1]  # best histogram slope bounds
        SEPARATION = self.best_grouped_slopes[2]  # best histogram's bucket width
        NUM_CIRCLES = np.shape(self.best_cluster)[0]  # The number of circles

        # Find Slope with Most Parallels
        bucket_ind = np.argmax(SLOPE_HEIGHTS)  # highest segment of histogram
        parallel = SLOPE_BOUNDS[bucket_ind] - (
            SEPARATION / 2
        )  # slope at highest segment minus half bucket width is main parallel

        # Find Holes Associated with parallels
        idx = 0
        hole_idx = 0
        for slope in self.best_slopes:
            if np.abs(slope - parallel) <= SEPARATION:
                # x and y are the indexes of 2 circles corresponding to a slope
                x = idx // (NUM_CIRCLES - 1)
                y = idx % (NUM_CIRCLES - 1)
                y += int(y >= x)

                if hole_idx == 0:
                    self.holes = np.array(self.best_cluster[x])
                else:
                    self.holes = np.append(self.holes, self.best_cluster[x])

                self.holes = np.append(self.holes, self.best_cluster[y])
                hole_idx += 1
            idx += 1

        self.holes = self.holes.reshape((-1, 3))
        self.holes = np.unique(self.holes, axis=0)  # remove duplicates
        return self.holes

    def _group_slopes(self, slopes: np.ndarray) -> tuple:
        """
        Bucket sort slopes to find parallels.

        Parameters
        ----------
        slopes: np.ndarray
            Slopes data to use for bucket sorting

        Returns
        -------
        tuple - (slope_heights, slope_bounds, bucket_width) - histogram of slopes with bucket width
        """
        BUCKET_MODIFIER = 2  # Changes how many buckets are in the range
        NUM_SLOPES = np.shape(slopes)[0]  # The number of slopes

        # Get parameters for bucket sorting
        upper_bound = np.amax(slopes)
        lower_bound = np.amin(slopes)

        interquartile_range: np.float64 = np.percentile(slopes, 75) - np.percentile(
            slopes, 25
        )
        bucket_width: np.float64 = (2 * interquartile_range) / (
            NUM_SLOPES ** (1 / 3)
        )  # Freedman–Diaconis rule
        num_buckets: int = (
            int(round((upper_bound - lower_bound) / bucket_width)) + BUCKET_MODIFIER
        )

        # Bucket sort
        slope_heights, slope_bounds = np.histogram(
            slopes, num_buckets, (lower_bound, upper_bound)
        )

        result_bucket_width = (upper_bound - lower_bound) / (
            num_buckets
        )  # width of a bucket

        return (slope_heights, slope_bounds, result_bucket_width)

    def _get_slopes(self, circles: np.ndarray) -> np.ndarray:
        """
        Finds slopes between circles.

        Parameters
        ----------
        circles: np.ndarray
            Array of circles to get the slopes of

        Returns
        -------
        np.ndarray - Array of calculated slopes between circles
        """
        slopes = np.array([])
        for x, y, _ in circles:
            for iX, iY, _ in circles:
                m = (iY - y) / (iX - x)
                # slope must be non-infinite and can't be between the same circle
                if (not np.isnan(m)) and (not np.isinf(m)) and (x != iX and y != iY):
                    slopes = np.append(slopes, m)

        # Convert slopes to degrees
        slopes = np.degrees(np.arctan(slopes))

        return slopes

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
        median_brightness = np.median(gray)  # median brightness of gray scale image

        if not median_brightness:  # prevent divide by zero
            median_brightness = 1

        # Calculate magnitude of brightness based on median + offset
        alpha_value = (128 + offset) / median_brightness

        # Brighten image
        brightened_image = cv2.addWeighted(
            src1=self.img, alpha=alpha_value, src2=0, beta=0, gamma=0
        )  # brightened_image = src1*alpha + src2*beta + gamma

        return brightened_image

    def _filter_text_circles(self) -> np.ndarray:
        """
        Filters out circles that are to the left of, right of, or above set text.

        Returns
        -------
        np.ndarray - filtered array of circles
        """
        MIN_TEXTBOXES = 1  # minimum number of text boxes tolerated
        MAX_TEXTBOXES = 2  # maximum (or ideal) number of text boxes tolerated
        PADDING_CONST = (
            0.5  # amount of padding to apply if only MIN_TEXTBOXES text boxes is found
        )
        ROTNEG90 = np.array([[0, 1], [-1, 0]])  # matrix to rotate a vector -90 degrees

        # Too low confidence if too little or too many text boxes found
        if len(self.text_boxes) < MIN_TEXTBOXES or len(self.text_boxes) > MAX_TEXTBOXES:
            return self.circles

        # Filter out rectangles that are not directly below text
        circle_filter = np.array(
            [], dtype=np.uint16
        )  # array of indices of circles out of bounds

        # get text bounding extreme points of rotated bounding boxes
        ll_x, ll_y = self.text_boxes[0].vertices[0]  # lower left point
        lr_x, lr_y = self.text_boxes[-1].vertices[3]  # lower right point

        # if only minimum text boxes detected, add padding around text box equal to 1/2 the width of text
        if len(self.text_boxes) == MIN_TEXTBOXES:
            lb_vect = (lr_x - ll_x, lr_y - ll_y)
            # lower left bound with extra padded distance = normal lower left point - padding
            ll_x, ll_y = np.array((ll_x, ll_y)) - np.int0(
                np.array(lb_vect) * (PADDING_CONST)
            )
            # lower right bound with extra padded distance = padding + normal lower right point
            lr_x, lr_y = np.int0(np.array(lb_vect) * (PADDING_CONST)) + np.array(
                (lr_x, lr_y)
            )

        # vector along lower bound of text
        lower_vect = (lr_x - ll_x, lr_y - ll_y)

        # vector perpendicular to lower_vect used as left and right bounds for circle filter
        perp_vect = tuple(np.dot(lower_vect, ROTNEG90).astype(int))

        # create a vector from the lower-left/lower-right corner of text to all detected circles
        # the cross product tells us what side of the bounding vectors the circle is on
        for i, (x, y, _) in enumerate(self.circles):
            needs_removal = False  # assume the circle is safely below the text

            # create two vectors
            ll_to_circ = (x - ll_x, y - ll_y)  # vector from ll bound to circle
            lr_to_circ = (x - lr_x, y - lr_y)  # vector from lr bound to circle

            lower_cross = np.cross(lower_vect, ll_to_circ)  # <0 = above lower bound
            if lower_cross <= 0:
                needs_removal = True
            left_cross = np.cross(perp_vect, ll_to_circ)  # >0 = outside left bound
            if left_cross >= 0:
                needs_removal = True
            right_cross = np.cross(perp_vect, lr_to_circ)  # <0 = outside right bound
            if right_cross <= 0:
                needs_removal = True

            if needs_removal:
                circle_filter = np.append(circle_filter, i)

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
        np.ndarray - filtered array of circles
        """
        # Create filter of far away circles based on depth image
        circle_filter = np.array(
            [], dtype=np.uint16
        )  # array of indices of distant circles

        for i, (x, y, _) in enumerate(self.circles):
            if (
                self.depth[y][x] > depth_threshold
            ):  # if too far away, remove (add index to filter)
                circle_filter = np.append(circle_filter, i)

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
        MAX_COMPACTNESS = 40000  # NOTE: May need scaling up for higher res, only tested with 480p Data
        MIN_COMPACTNESS = (
            1000  # At this level, we're likely splitting up a potentially good cluster
        )
        MAX_CLUSTERS = 30

        if self.circles.shape[0] < 5:  # not enough circles for clustering
            # place all circles into one cluster
            num_clusters = 1
            labels = np.zeros(self.circles.shape[0], dtype=np.ushort)
        else:
            num_clusters = 2
            kmeans_circles = self.circles.astype(
                np.float32
            )  # kmeans requires float32 data

            compactness = MAX_COMPACTNESS + 1  # init compactness to enter while loop
            while compactness > MAX_COMPACTNESS:  # ensure low variance within clusters
                # perform clustring with current num_clusters
                compactness, labels, _ = cv2.kmeans(
                    data=kmeans_circles,
                    K=num_clusters,
                    bestLabels=None,
                    criteria=CLSTR_CRITERIA,
                    attempts=30,
                    flags=cv2.KMEANS_PP_CENTERS,
                )

                # too many clusters = too low confidence for further clustering
                if num_clusters > MAX_CLUSTERS:
                    return
                # or circles are already super compact = likely overlapping
                if compactness < MIN_COMPACTNESS:
                    self.clusters = [self.circles]
                    return
                # attempt more clusters if clusters too spread out
                if compactness > MAX_COMPACTNESS:
                    num_clusters += 1  # try higher K value

            labels = np.ravel(labels)  # flatten column vector of labels

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
        # Remove circles that are farther than DEPTH_THRESHOLD millimeters away
        self._filter_distant_circles(DEPTH_THRESH)

        # Remove circles that aren't directly below text
        self._filter_text_circles()

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
        self.best_grouped_slopes = (np.array([0]), np.array([0]), 0)

        self.center = np.arange(2)
        self.holes = np.zeros((4, 3), dtype=np.uint16)

        self.text_boxes = []

        self.needs_recalc = True

    def set_text(self, text_boxes: list) -> None:
        """
        Sets the BoundingBoxes of the text in the image.

        Parameters
        ----------
        text_boxes: list[BoundingBox]
            The BoundingBoxes of the text in the image.

        Returns
        -------
        None
        """
        # Set text boxes
        self.text_boxes = text_boxes

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
                color = np.random.choice(256, size=3)
                color = (int(color[0]), int(color[1]), int(color[2]))
                thickness = 1
                if np.array_equal(
                    cluster, self.best_cluster
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
                color = np.random.choice(256, size=3)
                color = (int(color[0]), int(color[1]), int(color[2]))
                thickness = 1
                if np.array_equal(
                    cluster, self.best_cluster
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
