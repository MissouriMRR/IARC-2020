"""
For testing all module algorithms.
"""
import os, sys, time

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
gggparent_dir = os.path.dirname(ggparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir, gggparent_dir]

import numpy as np
import cv2

from vision.bounding_box import BoundingBox, ObjectType

from vision.module.location import ModuleLocation
from vision.module.get_module_depth import get_module_depth
from vision.module.region_of_interest import region_of_interest
from vision.module.module_bounding import getModuleBounds
from vision.module.module_orientation import get_module_orientation
from vision.module.module_orientation import get_module_roll


IMG_FOLDER = "module"  # default folder to read images from


class AccuracyModule:
    """
    Testing accuracy of module algorithms.
    """

    def __init__(self):
        self.location = ModuleLocation()

    def accuracy_isInFrame(
        self, color_image: np.ndarray, depth_image: np.ndarray
    ) -> bool:
        """
        Measuring accuracy of isInFrame() from ModuleLocation class.

        Parameters
        ----------
        color_image: ndarray
            The color image.
        depth_image: ndarray
            The depth image.

        Returns
        -------
        bool - whether the module was detected in color_image.
        """
        self.location.setImg(color_image, depth_image)
        return self.location.isInFrame()

    def accuracy_getCenter(
        self, color_image: np.ndarray, depth_image: np.ndarray, set_img: bool = False
    ) -> tuple:
        """
        Measuring accuracy of isInFrame() from ModuleLocation class.

        Parameters
        ----------
        color_image: ndarray
            The color image.
        depth_image: ndarray
            The depth image.
        set_img: bool
            Whether or not to set the image in the location class.
            Defaults to False, which assumes image has already been set when isInFrame was benchmarked.

        Returns
        -------
        tuple - (x, y) coordinates of the center of the module in color_image.
        """

        if set_img:
            self.location.setImg(color_image, depth_image)
        return self.location.getCenter()

    def accuracy_get_module_depth(
        self, depth_image: np.ndarray, center: tuple
    ) -> float:
        """
        Measuring accuracy of get_module_depth().

        Parameters
        ----------
        depth_image: ndarray
            The depth image.
        center: tuple
            (x, y) coordinates of the center of the module.

        Returns
        -------
        float: Depth value at the center of the module in millimeters.
        """
        return get_module_depth(depth_image, center)

    def accuracy_region_of_interest(
        self, depth_image: np.ndarray, depth_val: np.ndarray, center: tuple
    ) -> np.ndarray:
        """
        Measuring accuracy of region_of_interest().

        Parameters
        ----------
        depth_image: ndarray
            The depth image.
        depth_val: float
            Measured value of the depth of the module.
        center: tuple
            (x, y) coordinates of the center of the module.

        Returns
        -------
        ndarray - Region of depth image.
        """
        return region_of_interest(depth_image, depth_val, center)

    def accuracy_get_module_orientation(self, roi: np.ndarray) -> tuple:
        """
        Measuring accuracy of get_module_orientation().

        Parameters
        ----------
        roi: ndarray
            The module region of interest calculated by region_of_interest().

        Returns
        -------
        tuple - (x_tilt, y_tilt) orientation of module
        """
        return get_module_orientation(roi)

    def accuracy_getModuleBounds(
        self, dimensions: tuple, center: tuple, depth: float
    ) -> list:
        """
        Measuring accuracy of getModuleBounds.

        Parameters
        ----------
        dimensions: tuple
            The dimensions of the color image.
        center: tuple
            (x, y) coordinates of center of module.
        depth: float
            Depth value at center of module.

        Returns
        -------
        list<tuple> - list of four (x, y) vertices around padded module.
        """
        return getModuleBounds(dimensions, center, depth)

    def accuracy_get_module_roll(self, region: np.ndarray) -> float:
        """
        Measuring accuracy of get_module_roll().

        Parameters
        ----------
        region: ndarray
            Padded region of image with module.

        Returns
        -------
        float - module roll with respect to positive y-axis.
        """
        return get_module_roll(region)

class BenchModuleAccuracy:
    """
    Object for storing parameters of and running the module accuracy benchmark.

    Parameters
    ----------
    draw_circles: bool
        Whether to save an image with the circles found by location class.
    draw_centers: bool
        Whether to save an image with the center found by the getCenter function from the location class.
    """
    def __init__(self, draw_circles: bool = False, draw_center: bool = False):
        self.draw_circles = draw_circles
        self.draw_center = draw_center

    def set_parameters(self, draw_circles: bool = False, draw_center: bool = False) -> None:
        """
        Sets the parameters for running the benchmark.
        
        Parameters
        ----------
        draw_circles: bool
            Whether to save an image with the circles found by location class.
        draw_centers: bool
            Whether to save an image with the center found by the getCenter function from the location class.

        Returns
        -------
        None
        """
        self.draw_circles = draw_circles
        self.draw_center = draw_center
        return

    def bench_accuracy(
        self,
        folder: str,
        file_output,
        tester: AccuracyModule,
        image: np.ndarray,
        depth: np.ndarray,
        filename: str,
    ) -> bool:
        """
        Runs all module accuracy benchmarks on all images in a specified folder.
        Outputs results to csv file

        Parameters
        ----------
        folder: str
            The folder of images to test.
        file_output: IO
            File stream to output results to.
        tester: AccuracyModule
            Benchmark class to use. Initialized elsewhere to be static between image runs.
        image: np.ndarray
            The color image from the frame.
        depth: np.ndarray
            The depth image from the frame.
        filename: str
            The name of the image file.

        Returns
        -------
        bool - whether all tests were completed.
        """
        OUTPUT_IMGS_DIR = "marked_images"  # Folder to output saved images to if necessary

        crash = False  # Whether an algorithm crashed

        ## Run tests on the image ##

        in_frame = False
        # isInFrame
        if not crash:
            try:
                in_frame = tester.accuracy_isInFrame(image, depth)
                file_output.write(str(in_frame))
            except:
                file_output.write("Crash")
                crash = True

        file_output.write(",")

        # getCenter
        center = (0, 1)
        if in_frame and not crash:  # only runs further tests if in frame
            try:
                center = tester.accuracy_getCenter(image, depth)
                file_output.write(str(center[0]) + " . " + str(center[1]))
            except:
                file_output.write("Crash")
                crash = True
        file_output.write(",")

        # get_module_depth
        depth_val = 0.0
        if center != (0, 1) and not crash:  # only runs further tests if center found
            try:
                depth_val = tester.accuracy_get_module_depth(depth, center)
                file_output.write(str(depth_val))
            except:
                file_output.write("Crash")
                crash = True
        file_output.write(",")

        # region_of_interest
        roi = np.ndarray([])
        if depth_val != 0 and not crash:
            try:
                roi = tester.accuracy_region_of_interest(depth, depth_val, center)
                file_output.write("Found")
            except:
                file_output.write("Crash")
                crash = True
        file_output.write(",")

        # get_module_orientation
        orientation = (0, 0)

        if crash:
            file_output.write("Dependency Crash")

        if depth_val != 0 and not crash:
            try:
                orientation = tester.accuracy_get_module_orientation(roi)
                file_output.write(str(orientation[0]) + " . " + str(orientation[1]))
            except:
                file_output.write("Crash")
                crash = True
        file_output.write(",")

        # getModuleBounds
        bounds = np.ndarray([])
        if depth_val != 0 and not crash:
            try:
                bounds = tester.accuracy_getModuleBounds((1920, 1080), center, depth_val)
                file_output.write("Found")
            except:
                file_output.write("Crash")
                crash = True
        file_output.write(",")

        # get_module_roll
        roll = 0.0

        if crash:
            file_output.write("Dependency Crash")

        if depth_val != 0 and not crash:
            try:
                bound_region = image[
                    bounds[0][1] : bounds[3][1], bounds[0][0] : bounds[3][0], :
                ]
                roll = tester.accuracy_get_module_roll(bound_region)
                file_output.write(str(roll))
            except:
                file_output.write("Crash")
                crash = True
        file_output.write(",")

        # Saves image with circles and, if enabled, center
        if self.draw_circles or self.draw_center:
            path = os.path.join(OUTPUT_IMGS_DIR, filename)
            tester.location.saveImage(file=path, draw_circles=self.draw_circles, draw_center= self.draw_center)

        return crash


if __name__ == "__main__":
    """
    Runs bench_module_accuracy() to test all module accuracy benchmarks.
    Defaults to IMG_FOLDER if no folder is specified.
    Will only run on images that have an .npy extension associated depth image.

    Command Line Arguments
    -f, --folder {foldername}
        folder in module folder to run accuracy benchmarks on.
    -q, --quiet
        produce no output while running
    -c, --draw-centers
        draw a red circle in the calculated centers of each image, stored in ./marked_images

    """
    import argparse

    # handle argument parsing
    parser = argparse.ArgumentParser(
        description="To use a specific directory, use -f (folder)"
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="outputs no file information while running",
    )
    parser.add_argument(
        "-f",
        "--folder",
        type=str,
        help="folder name in the vision_images/module directory",
    )
    parser.add_argument(
        "-s",
        "--save-circles",
        action="store_true",
        help="creates a folder that saves images with circles of which the module is in frame",
    )
    parser.add_argument(
        "-c",
        "--save-centers",
        action="store_true",
        help="draws a red circle in the center for each image, stored in ./marked_images",
    )
    args = parser.parse_args()

    # default folder
    folder = IMG_FOLDER

    # change folder if specified
    if args.folder:
        folder = args.folder

    # run accuracy benchmarks
    bench_module_accuracy(folder, args.quiet, args.save_circles, args.save_centers)
