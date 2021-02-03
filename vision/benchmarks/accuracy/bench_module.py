"""
For testing all module algorithms.
"""
import os, sys

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
gggparent_dir = os.path.dirname(ggparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir, gggparent_dir]

import numpy as np
import cv2

from vision.bounding_box import BoundingBox, ObjectType

from vision.module.location import ModuleLocation
from vision.module.region_of_interest import region_of_interest as roi
from vision.module.module_orientation import get_module_orientation


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

        Returns
        -------
        bool - whether the module was detected in color_image
        """
        self.location.setImg(color_image, depth_image)
        return self.location.isInFrame()

    def accuracy_getCenter(
        self, color_image: np.ndarray, depth_image: np.ndarray
    ) -> tuple:
        """
        Measuring accuracy of isInFrame() from ModuleLocation class.

        Returns
        -------
        tuple - (x, y) coordinates of the center of the module in color_image.
        """
        self.location.setImg(color_image, depth_image)
        return self.location.getCenter()


def bench_module_accuracy(folder: str) -> None:
    """
    Runs all module accuracy benchmarks for a specified folder.

    Returns
    -------
    None
    """
    tester = AccuracyModule()
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".jpg"):
                # Attempt to read the file
                filename = os.path.join(root, file)
                depthname = filename[:-14] + "depthImage.npy"

                image = np.array([])
                depth = np.array([])

                try:
                    image = cv2.imread(filename)
                except:
                    print("Failed to read image:", filename)
                    return
                try:
                    depth = np.load(depthname)
                except:
                    print("Failed to read image:", depthname)
                    return
                
                if image is None:
                    print("Failed to read image:", filename)
                    return
                if depth is None:
                    print("Failed to read image:", depthname)
                    return

                # Run tests on the image
                print(filename)
                result = tester.accuracy_isInFrame(image, depth)
                print("isInFrame:", result)
                result = tester.accuracy_getCenter(image, depth)
                print("getCenter:", result)

    return


if __name__ == "__main__":
    """
    Runs bench_module_accuracy() to test all module accuracy benchmarks.
    Defaults to IMG_FOLDER if no folder is specified.
    Will only run on images that have an .npy extension associated depth image.

    Command Line Arguments
    -f {foldername}
        folder in module folder to run accuracy benchmarks on.
    """
    import argparse

    # handle argument parsing
    parser = argparse.ArgumentParser(
        description="To use a specific directory, use -f (folder)"
    )
    parser.add_argument(
        "-f",
        "--folder",
        type=str,
        help="folder name in the vision_images/module directory",
    )
    args = parser.parse_args()

    # default folder
    folder = IMG_FOLDER

    # change folder if specified
    if args.folder:
        folder = args.folder

    # run accuracy benchmarks
    bench_module_accuracy(folder)
