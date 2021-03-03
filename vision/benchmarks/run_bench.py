"""
Run a benchmark on a specified image folder or bag file.
"""

import os, sys

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
gggparent_dir = os.path.dirname(ggparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir, gggparent_dir]

import numpy as np
import cv2

from vision.camera.bag_file import BagFile

# .bag file constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FRAME_RATE = 60
REPEAT = False # Whether to continously run through a .bag file test

def run_set(bench_name: str, folder: str) -> None:
    """
    Run a dataset of color and depth images through a benchmark.

    Parameters
    ----------
    bench_name: str
        The name of the benchmark to run
    folder: str
        The directory of the dataset.
    """
    if bench_name == "module":
        pass
    elif bench_name == "obstacle":
        pass
    elif bench_name == "pylon":
        pass
    elif bench_name == "text":
        pass
    return

def run_bag_stream(self, bench_name: str, filename: str) -> None:
    """
    Run the .bag file in "real time" through a benchmark.
    NOTE: Since the file is being run as a stream, the number of frames processed
            will depend on the speed of the algorithms being benchmarked.

    Parameters
    ----------
    bench_name: str
        The name of the benchmark to run.

    Returns
    -------
    None
    """
    stream = BagFile(SCREEN_WIDTH, SCREEN_HEIGHT, FRAME_RATE, filename, REPEAT)

    if bench_name == "module":
        pass
    elif bench_name == "obstacle":
        pass
    elif bench_name == "pylon":
        pass
    elif bench_name == "text":
        pass
    return

def run_bag_set(self, bench_name: str, filename: str, folder_name: str = "new_set") -> None:
    """
    Saves bag file as dataset of images before sending dataset to specified benchmark.
    NOTE: Due to how .bag file is read, the number of frames saved may vary. Not every frame of the file is saved.
            Will still get more frames than when running as stream,
            since number of frames does not depend on algorithms being benchmarked.

    Parameters
    ----------
    bench_name: str
        The name of the benchmark to run.
    filename: str
        The name of the .bag file.
    folder_name: str
        The folder to save the new dataset to, relative to vision_images.

    Returns
    -------
    None
    """
    REPEAT = False # Whether to continously run through the bag file (True will cause infinite image generation)

    # Create the data set from the bag file.
    BagFile(SCREEN_WIDTH, SCREEN_HEIGHT, FRAME_RATE, filename, REPEAT).save_as_img(folder_name)

    if bench_name == "module":
        pass
    elif bench_name == "obstacle":
        pass
    elif bench_name == "pylon":
        pass
    elif bench_name == "text":
        pass
    return

def run_bench(bench_name: str, file_loc: str, dataset_bag: bool = False):
    """
    Runs the specified benchmark on an image folder or bag file.

    Parameters
    ----------
    bench_name: str
        The name of the benchmark to run.
    file_loc: str
        The directory of the image folder or bag file to run the benchmark on.
    dataset_bag: bool
        For .bag files. Whether to create and iterate through data set of images.
    
    Returns
    -------
    None
    """
    if file_loc[-4:] == ".bag": # running on bag file
        if dataset_bag:
            run_bag_set(bench_name, file_loc)
        else:
            run_bag_stream(bench_name, file_loc)
    
    else: # running on image directory
        run_set(bench_name, file_loc)

if __name__ == "__main__":
    """
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Must specify benchmark name and file location."
    )

    # handle argument parsing
    parser.add_argument(
        "-b",
        "--bench_name",
        type=str,
        help="Name of the benchmark to run. Can be module, obstacle, pylon, or text.",
    )
    parser.add_argument(
        "-f",
        "--file_location",
        type=str,
        help="Location of the .bag file to run or the folder of the data set to run.",
    )

    parser.add_argument(
        "-d",
        "--dataset_bag",
        action="store_true",
        help="For use with .bag files. Enables creation of and iteration through data set of images."
    )

    args = parser.parse_args()

    # no benchmark name specified, cannot continue
    if not args.bench_name:
        raise RuntimeError("No benchmark specified.")

    # no file location specified, cannot continue
    if not args.file_location:
        raise RuntimeError("No file location specified.")

    run_bench("module", "file/folder/whatever", args.dataset_bag)