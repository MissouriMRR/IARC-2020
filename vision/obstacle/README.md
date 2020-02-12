# Obstacle Detection

The obstacle team is a division of the vision team dedicated to detecting
and classifying objects in images taken by the drone's RealSense cameras.

## Documentation

Obstacle detection is done with the OpenCV SimpleBlobDetector. 
The SimpleBlobDetector can take a number of parameters that control how the
blobs are detected, which are interpreted as obstacles. 
SimpleBlobDetector follows a number of steps in
order to find blobs:
(Summarized from [LearnOpenCV](learnopencv.com/blob-detection-using-opencv-python-c/))

 1. **Thresholding:** Multiple binary images are created from the source image, where binarization is done in the range of `minThreshold` and `maxThreshold` for each image.

 2. **Grouping:** In each of the binary images, connected white pixels are grouped.

 3. **Merging:** The centers of the groups are compared. If the blobs are closer together than `minDistBetweenBlobs`, then they are merged together.

 4. **Center and Radius:** Finally, each blob has its center and radius computed.

The return value is a list of [keypoints](docs.opencv.org/2.4/modules/features2d/doc/common_interfaces_of_feature_detectors.html#keypoint), 
where each `KeyPoint` contains the center of a blob as a `Point2f pt` and the
diameter of the blob as a `float size`.

The find_blobs function takes in an image (with optional logging), and returns
an `np.array` of `Rectangle` objects that define the bounding boxes of the blobs.

## Unit Testing

Unit tests can be found under [vision/unit_tests](vision/unit_tests).
There is a unit test called `test_obstacle_detection` that tests all the
images in [vision/vision_images/obstacle](vision/blob/samples) to determine if the
expected number of obstacles is actually detected. Note that this requires modifying
the `expected_obstacles` array based on your images. A second test called 
`test_params_import` is used to verify that custom parameters for the `ObstacleFinder`
are imported correctly.
