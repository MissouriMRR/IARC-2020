# Module
These are tools for helping the drone pick up and manipulate the module.

## ModuleInFrame
The ModuleInFrame function will take in an image path as a string.

It will read in the image and reshape it to remove the depth channel.
It will grayscale the image and apply a gaussian blur.
It will then apply a laplacian transform and run hough circle detection to find the holes in the module.

It will then find the slopes between the center of the circles and store the slopes in a dictionary.
Then, it will detect the number of pairs of parallel slopes that are in the dictionary. Two slopes are considered parallel if they are within .01 of eachother.
If more than 300 pairs of parallel slopes are detected, the function will return True. It will return False otherwise.

## ModuleKMeans
The ModuleKMeans class allows the user to take an image and isolate certain color channels
using the KMeans algorithm. This can be used as a baseline for detecting when the module is
in frame.
