"""
Boat related unit tests.
"""
import os, sys
from io import IOBase

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
gggparent_dir = os.path.dirname(ggparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir, gggparent_dir]

import numpy as np

from text.detect_words import TextDetector

IMG_FOLDER = 'text'

class AccuracyRussianWord:
    """
    Measuring accuracy of the text detector.
    """
    def __init__(self):
        self.setup()

    def setup(self) -> None:
        """
        Benchmark setup.

        Returns
        -------
        None
        """
        self.text_detector = TextDetector()

    def accuracy_detector(self, color_image: np.ndarray, depth_image: np.ndarray) -> list:
        """
        Accuracy of detectRussianWord.

        Returns
        -------
        List[BoundingBox]
        """
        return self.text_detector.detect_russian_word(color_image=color_image, depth_image=depth_image)

class BenchTextAccuracy:
    """
    Object for storing parameters of and running the text accuracy benchmark.
    """
    def __init__(self):
        self.OUTPUT_IMGS_DIR = "marked_images"  # Folder to output saved images to if necessary
        self.OUTPUT_RESULTS_DIR = "results" # Folder to output resulting BoundingBoxes to

        if not os.path.isdir(self.OUTPUT_IMGS_DIR):
            os.mkdir(self.OUTPUT_IMGS_DIR)
        if not os.path.isdir(self.OUTPUT_RESULTS_DIR):
            os.mkdir(self.OUTPUT_RESULTS_DIR)
    
    def set_parameters(self) -> None:
        """
        Sets the parameters for running the benchmark.

        Returns
        -------
        None
        """
        return

    def bench_accuracy(
        self,
        folder: str,
        file_output: IOBase,
        tester: AccuracyRussianWord,
        image: np.ndarray,
        depth: np.ndarray,
        filename: str
    ) -> bool:
        """
        Runs all text detection accuracy benchmarks on an image. Outputs results to csv file.

        Parameters
        ----------
        folder: str
            The folder of images to test.
        file_output: IO
            File stream to output results to.
        tester: AccuracyRussianWord
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

        ## Run tests on the image ##

        bboxes = []
        # detect_russian_word
        if not crash:
            try:
                bboxes = tester.accuracy_detector(color_image=image, depth_image=depth)

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
        
        return crash