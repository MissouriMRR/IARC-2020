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
        self, color_image: np.ndarray, depth_image: np.ndarray
    ) -> tuple:
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
        tuple - (x, y) coordinates of the center of the module in color_image.
        """
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


def bench_module_accuracy(
    folder: str,
    quiet_output: bool = False,
    draw_circles: bool = False,
    draw_centers: bool = False,
) -> None:
    """
    Runs all module accuracy benchmarks on all images in a specified folder.
    Outputs results to csv file

    Parameters
    ----------
    folder: str
        The folder of images to test.

    Returns
    -------
    None
    """
    OUTPUT_FILE = "results.csv"
    OUTPUT_IMGS_DIR = "marked_images"

    f = open(
        OUTPUT_FILE, "w"
    )  # will overwrite existing file, backup previous results if needed
    
    if (draw_centers or draw_circles) and not os.path.isdir(OUTPUT_IMGS_DIR):
        os.mkdir(OUTPUT_IMGS_DIR)

    f.write(
        "image,read color,read depth,isInFrame(),getCenter(),get_module_depth(),region_of_interest(),get_module_orientation(),getModuleBounds(),get_module_roll(),exec time (s)\n"
    )

    total_imgs = sum(".jpg" in s for s in os.listdir(folder))
    total_time = 0
    file_counter = 0

    tester = AccuracyModule()
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".jpg"):
                file_counter += 1
                crash = False  # whether the current image crashed at some point

                # Attempt to read the file
                filename = os.path.join(root, file)
                depthname = filename[:-14] + "depthImage.npy"

                image = np.array([])
                depth = np.array([])

                f.write(filename + ",")

                try:
                    image = cv2.imread(filename)
                except:
                    f.write("False")
                    crash = True
                if image is None:
                    f.write("False")
                    crash = True
                f.write("True,")

                try:
                    depth = np.load(depthname)
                except:
                    f.write("False")
                    crash = True
                if depth is None:
                    f.write("False")
                    crash = True
                f.write("True,")

                in_frame = False

                # Run tests on the image

                # get start time of image processing
                start_time = time.time()

                # isInFrame
                if not crash:
                    try:
                        in_frame = tester.accuracy_isInFrame(image, depth)
                        f.write(str(in_frame))
                    except:
                        f.write("Crash")
                        crash = True

                f.write(",")

                # getCenter
                center = (0, 1)
                if in_frame and not crash:  # only runs further tests if in frame
                    try:
                        center = tester.accuracy_getCenter(image, depth)
                        f.write(str(center[0]) + " . " + str(center[1]))
                    except:
                        f.write("Crash")
                        crash = True
                f.write(",")

                # get_module_depth
                depth_val = 0.0
                if (
                    center != (0, 1) and not crash
                ):  # only runs further tests if center found
                    try:
                        depth_val = tester.accuracy_get_module_depth(depth, center)
                        f.write(str(depth_val))
                    except:
                        f.write("Crash")
                        crash = True
                f.write(",")

                # region_of_interest
                roi = np.ndarray([])
                if depth_val != 0 and not crash:
                    try:
                        roi = tester.accuracy_region_of_interest(
                            depth, depth_val, center
                        )
                        f.write("Found")
                    except:
                        f.write("Crash")
                        crash = True
                f.write(",")

                # get_module_orientation
                orientation = (0, 0)

                if crash:
                    f.write("Dependency Crash")

                if depth_val != 0 and not crash:
                    try:
                        orientation = tester.accuracy_get_module_orientation(roi)
                        f.write(str(orientation[0]) + " . " + str(orientation[1]))
                    except:
                        f.write("Crash")
                        crash = True
                f.write(",")

                # getModuleBounds
                bounds = np.ndarray([])
                if depth_val != 0 and not crash:
                    try:
                        bounds = tester.accuracy_getModuleBounds(
                            (1920, 1080), center, depth_val
                        )
                        f.write("Found")
                    except:
                        f.write("Crash")
                        crash = True
                f.write(",")

                # get_module_roll
                roll = 0.0

                if crash:
                    f.write("Dependency Crash")

                if depth_val != 0 and not crash:
                    try:
                        bound_region = image[
                            bounds[0][1] : bounds[3][1], bounds[0][0] : bounds[3][0], :
                        ]
                        roll = tester.accuracy_get_module_roll(bound_region)
                        f.write(str(roll))
                    except:
                        f.write("Crash")
                        crash = True
                f.write(",")

                end_time = time.time()

                # calculate execution time
                exec_time = end_time - start_time
                f.write(str(exec_time))

                total_time += exec_time

                # std output of file processing
                if not quiet_output:
                    print(
                        "FILE (" + str(file_counter) + "/" + str(total_imgs) + "):",
                        file,
                        "TIME:",
                        "{:.3f}".format(exec_time),
                        "CRASH:",
                        crash,
                    )
                    
                # Saves image with circles and, if enabled, center
                if draw_circles or draw_centers:
                    path = os.path.join(OUTPUT_IMGS_DIR, file)
                    tester.location.saveCircleImage(path, draw_centers)

                f.write("\n")

        avg_time = total_time / total_imgs
        f.write("\nAvg Time (s): " + str(avg_time) + "\n")
        f.write("Total Time (s): " + str(total_time) + "\n")

        if not quiet_output:
            print("\nAverage Time (s):", avg_time)
            print("Total Time (s):", total_time)

    f.close()
    return


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