"""
This class is designed to take an image and binarize it based on what colors
we need to see.
"""
import numpy as np
import cv2


## NOTE: Unmaintained, no plans to use in final.


class ModuleKMeans:
    """
    Applies the kmeans algorithm to an image and displays a remapped
    version of the image showing either the remapped colors or a black
    and white image showing only specified color channels

    Paramters
    ---------
    channel_weights: float array
        Decides the weight of each channel in the image
    """

    def __init__(self, channel_weights=None):
        self.channel_weights = (
            channel_weights if channel_weights is not None else [1.0, 1.0, 1.0]
        )

    def applyKMeans(
        self, image, K, criteria=0, attempts=10, flags=cv2.KMEANS_RANDOM_CENTERS
    ):
        """
        Applies the kmeans algorithm to the image

        Parameters
        ----------
        image: ndarray
            Image to apply kmeans to.

        K: int
            Number of centers to use for the kmeans algorithm
            (bigger K = more variety of colors)

        criteria: tuple
            KMeans termination criteria. When one of the criteria is satisfied,
            the KMeans algorithm stops.

            type: Either cv2.TERM_CRITERIA_EPS (algorithm will terminate when
            specified epsilon value is met), cv2.TERM_CRITERIA_MAX_ITER
            (algorithm will terminate when specified number of iterations is
            met), or cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER (both)

            max_iter: An integer specifying the max number of iterations

            epsilon: A float representing the max accuracy

        attempts: int
            Number of times to generate different initial labellings

        flags: cv2.KMEANS_RANDOM_CENTERS/cv2.KMEANS_PP_CENTERS
            Specifies how initial labellings are taken (randomly or using
            kmeans++ center initialization, respectively)
        """

        self.img = image

        if image is None:
            raise ValueError(f"Image cannot be None.")

        if len(self.img.shape) == 3 and self.img.shape[-1] != len(self.channel_weights):
            raise ValueError(
                f"Image incorrect shape, expected: {len(self.channel_weights)} got {self.img.shape[-1]}"
            )

        if len(self.img.shape) == 2 and len(self.channel_weights) > 1:
            raise ValueError(
                f"Image incorrect shape, expected: {len(self.channel_weights)} got 1"
            )

        self.pixelData = self.img.reshape((-1, len(self.channel_weights)))
        self.pixelData = np.float32(self.pixelData)
        self.pixelData *= self.channel_weights

        if criteria == 0:
            criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)

        self.compactness, self.label, self.center = cv2.kmeans(
            self.pixelData, K, None, criteria, attempts, flags
        )

        return self.compactness, self.label, self.center

    def displayFractal(self):
        """
        Displays the remapped image with simplified colors
        """

        self.center = np.uint8(self.center)
        self.display = self.center[self.label.flatten()]
        self.display = self.display.reshape((self.img.shape))

        cv2.imshow("display", self.display)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    def displayBinary(self, channels):
        """
        Displays the image with only specified channels being white
        Parameters
        ----------
        channels: list of ints
            Channels specified in this parameter will be white while all
            others will be black
        """

        self.white = [255, 255, 255]
        # self.black = [0, 0, 0]

        # for i in self.label.reshape(self.img.shape[:2]):
        # self.img[self.label.reshape(self.img.shape[:2]) == i] = np.array(self.black)
        self.img = np.zeros(shape=self.img.shape)

        for i in channels:
            self.img[self.label.reshape(self.img.shape[:2]) == i] = np.array(self.white)

        cv2.imshow("img", self.img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


if __name__ == "__main__":
    """
    Testing Fractal and Binary KMeans Display

    Test images must be put in a file called vision_images
    """
    import os

    prefix = "vision" if os.path.isdir("vision") else ""
    filename = os.path.join(prefix, "vision_images", "module", "blocks1.jpg")
    image = cv2.imread(filename)
    if image is None:
        print(f"Failed to read image: {filename}")
        exit()

    print(image.shape)

    kmeans = ModuleKMeans()
    kmeans.applyKMeans(image, 3)

    kmeans.displayFractal()
    kmeans.displayBinary(channels=[0, 1])
