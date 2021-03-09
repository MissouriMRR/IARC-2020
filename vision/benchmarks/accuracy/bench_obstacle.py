"""
Obstacle detector unit tests.
"""
import os, sys
from io import IOBase

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
gggparent_dir = os.path.dirname(ggparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir, gggparent_dir]

import json
import numpy as np

from vision.common.import_params import import_params
from vision.common.box_plotter import plot_box

from vision.obstacle.obstacle_finder import ObstacleFinder
from vision.obstacle.obstacle_tracker import Obstacle, ObstacleTracker

IMG_FOLDER = "obstacle"


class AccuracyObstacle:
    """
    Measuring accuracy of obstacle detection.
    """

    def __init__(self):
        self.setup()

    def setup(self) -> None:
        """
        Setup obstacle detector via json file.

        Returns
        -------
        None
        """
        config_filename = os.path.join("vision", "obstacle", "config.json")

        with open(config_filename, "r") as config_file:
            config = json.load(config_file)

        self.obstacle_finder = ObstacleFinder(params=import_params(config))
        self.obstacle_tracker = ObstacleTracker()

    def accuracy_find(self, color_image: np.ndarray, depth_image: np.ndarray) -> list:
        """
        Test accuracy of obstacle finder.

        Parameters
        ----------
        color_image: np.ndarray
            The color image.
        depth_image: np.ndarray
            The depth image.

        Returns
        -------
        list<BoundingBox>
            A list of detected obstacles.
        """
        return self.obstacle_finder.find(color_image, depth_image)

    def acuracy_track(self, new_obstacles: list) -> list:
        """
        Test accuracy of obstacle tracker.

        Parameters
        ----------
        new_obstacles: list<BoundingBox>
            List of newly detected obstacles.

        Returns
        -------
        list<BoundingBox>
            A list of obstacles tracked between frames.
        """
        self.obstacle_tracker.update(new_obstacle_boxes=new_obstacles)
        return self.obstacle_tracker.getPersistentObstacles()


class BenchObstacleAccuracy:
    """
    Object for storing parameters of and running the obstacle accuracy benchmark.

    Parameters
    ----------
    plot_obs: bool
        Whether to plot obstacles on the image and save.
    """

    def __init__(self, plot_obs: bool = False):
        self.OUTPUT_IMGS_DIR = (
            "marked_images"  # Folder to output saved images to if necessary
        )
        self.OUTPUT_RESULTS_DIR = (
            "results"  # Folder to output resulting BoundingBoxes to
        )
        self.OUTPUT_FIND_DIR = os.path.join(self.OUTPUT_IMGS_DIR, "find")
        self.OUTPUT_TRACK_DIR = os.path.join(self.OUTPUT_IMGS_DIR, "track")

        self.plot_obs = plot_obs

        if not os.path.isdir(self.OUTPUT_IMGS_DIR):
            os.mkdir(self.OUTPUT_IMGS_DIR)
        if not os.path.isdir(self.OUTPUT_RESULTS_DIR):
            os.mkdir(self.OUTPUT_RESULTS_DIR)
        if not os.path.isdir(self.OUTPUT_FIND_DIR):
            os.mkdir(self.OUTPUT_FIND_DIR)
        if not os.path.isdir(self.OUTPUT_TRACK_DIR):
            os.mkdir(self.OUTPUT_TRACK_DIR)

    def set_parameters(self, plot_obs: bool = False) -> None:
        """
        Sets the parameters for running the benchmark.

        Returns
        -------
        None
        """
        self.plot_obs = plot_obs
        return

    def bench_accuracy(
        self,
        folder: str,
        file_output: IOBase,
        tester: AccuracyObstacle,
        image: np.ndarray,
        depth: np.ndarray,
        filename: str,
    ) -> bool:
        """
        Runs all obstacle accuracy benchmarks on an image. Outputs results to csv file.

        Parameters
        ----------
        folder: str
            The folder of images to test.
        file_output: IO
            File stream to output results to.
        tester: AccuracyObstacle
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
        crash = False
        output_bounding = open(
            os.path.join(self.OUTPUT_RESULTS_DIR, (filename[:-4] + ".txt")), "w"
        )

        ## Run tests on the image ##

        bboxes = []
        # obstacle detection
        if not crash:
            try:
                bboxes = tester.accuracy_find(color_image=image, depth_image=depth)

                # output BoundingBoxes to text file
                bbstr = [((b.__repr__()) + "\n") for b in bboxes]
                bbstr = "".join(bbstr)
                output_bounding.write(bbstr)
                output_bounding.write("\n\n")

                file_output.write("Found")

            except:
                file_output.write("Crash")
                crash = True
        file_output.write(",")

        if not crash and self.plot_obs:
            plot_box(boxes=bboxes, image=image, waittime=0, saveImg=self.plot_obs, path=os.path.join(self.OUTPUT_FIND_DIR, filename))

        # obstacle tracking
        if not crash:
            try:
                bboxes = tester.acuracy_track(new_obstacles=bboxes)

                # output BoundingBoxes to text file
                bbstr = [((b.__repr__()) + "\n") for b in bboxes]
                bbstr = "".join(bbstr)
                output_bounding.write(bbstr)
                output_bounding.write("\n\n")

                file_output.write("Found")
            except:
                file_output.write("Crash")
                crash = True
        file_output.write(",")

        if not crash and self.plot_obs:
            plot_box(boxes=bboxes, image=image, waittime=0, saveImg=self.plot_obs, path=os.path.join(self.OUTPUT_TRACK_DIR, filename))

        output_bounding.close()

        return crash
