# Module

The module team handles tasks related to the module. The main tasks are to find the location, distance to, and orientation of the module.
The goal of the module tasks is to allow flight to identify and manipulate the module.

## ModuleLocation  (location.py)

The ModuleLocation class will take in an image, determine whether it is in frame, and find the center of the module.

It will use circle detection combined with slope calculations to find the coordinates of the four holes on the front face.
Then, it will average these coordinates to find the center of the front face.
It will return the coordinates of the center.

## get_module_depth  (get_module_depth.py)

The get_module_depth function will return the depth to the module based on the coordinates of the center.
This depth is found by using the depth imformation in the depth image around center of the module.

## get_module_orientation and get_module_roll  (module_orientation.py)

The get_module_orientation function will calculate the orientation of the module in degrees
and return them as a tuple (x tilt, y tilt) using a derivative through the x- and y- axes of the depth image.

The get_module_roll function will calculate the z-tilt of the module using the contours of the image.

## region_of_interest  (region_of_interest.py)

The region_of_interest function will find a region of interest for the module for use in the orientation algorithm.
The region of interest is a region of the depth image based on an underestimate of the module.

## getModuleBounds  (module_bounding.py)

The getModuleBounds function will calculate and return the four vertices of the module based on an overestimate.
These vertices can be used to construct a BoundingBox for use in the pipeline.

## ModuleInFrame  (in_frame.py)

*NOTE: Unmaintained. See location.py for updated implementation*.

The ModuleInFrame function will determine if the module is in a frame.
This is determined using circle detection and slope calculations on these circles
to determine the likelyhood the module is in a frame.

## ModuleKMeans  (segmentation.py)

*NOTE: Not in use*.

The ModuleKMeans class allows the user to take an image and isolate certain color channels
using the KMeans algorithm. This can be used as a baseline for detecting when the module is
in frame.
