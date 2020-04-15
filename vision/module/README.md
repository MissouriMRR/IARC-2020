# Module

These are tools for helping the drone pick up and manipulate the module.

## ModuleInFrame  (in_frame.py)

The ModuleInFrame function will determine if the module is in a frame.
This is determined using circle detection and slope calculations on these circles
to determine the likelyhood the module is in a frame.

## ModuleLocation  (location.py)

The ModuleLocation class will take in an image and find the distance to the center of the module.

It will use circle detection combined with slope calculations to find the coordinates of the four holes on the front face.
Then, it will average these coordinates to find the center of the front face.
It will return the coordinates of the center.

## get_module_depth  (get_module_depth.py)

The get_module_depth function will return the depth to the module based on the coordinates of the center.
This depth is found by using the depth imformation in the depth image at the center of the module.

## get_module_orientation  (module_orientation.py)

The module_orientation function will calculate the orientation of the module in degrees
and return them as a tuple (x tilt, y tilt) using a derivative through the x- and y- axes.

## region_of_interest  (region_of_interest.py)

The region_of_interest function will find a region of interest for the module for use in the orientation algorithm.
The region of interest is a region of the depth image based on an underestimate of the module.

## getModuleBounds  (module_bounding.py)

The getModuleBounds function will calculate and return the four vertices of the module based on an overestimate.
These vertices can be used to construct a BoundingBox for use in the pipeline.

## ModuleKMeans  (segmentation.py)

*NOTE: Not in use*.

The ModuleKMeans class allows the user to take an image and isolate certain color channels
using the KMeans algorithm. This can be used as a baseline for detecting when the module is
in frame.