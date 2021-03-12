"""
Run a benchmark on a specified image folder or bag file.
"""

import os, sys, time
from io import IOBase

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
gggparent_dir = os.path.dirname(ggparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir, gggparent_dir]

import numpy as np
import cv2

from vision.camera.bag_file import BagFile

from vision.benchmarks.accuracy.bench_module import (
    BenchModuleAccuracy,
    AccuracyModule,
)
from vision.benchmarks.accuracy.bench_text import (
    BenchTextAccuracy,
    AccuracyRussianWord,
)
from vision.benchmarks.accuracy.bench_obstacle import (
    BenchObstacleAccuracy,
    AccuracyObstacle,
)

# .bag file constants
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FRAME_RATE = 60
REPEAT = False  # Whether to continously run through a .bag file test

# benchmark constants
OUTPUT_FILE = "results.csv"


def run_set(
    bench_name: str,
    folder: str,
    file_output: IOBase,
    quiet_output: bool = False,
    save_circles: bool = False,
    save_centers: bool = False,
    plot_boxes: bool = False,
) -> None:
    """
    Run a dataset of color and depth images through a benchmark.

    Parameters
    ----------
    bench_name: str
        The name of the benchmark to run
    folder: str
        The directory of the dataset.
    file_output: IOBase
        File output stream for results.
    quiet_output: bool
        Whether to silence terminal output.
    save_circles: bool
        For module benchmark. Whether to save images with circles plotted.
    save_centers: bool
        For module benchmark. Whether to save images with center plotted.
    plot_boxes: bool
        For text and obstacle benchmarks. Whether to save images with bounding boxes plotted.
    """

    benchmark = 0  # benchmark runner class
    tester = 0  # benchmark class
    if bench_name == "module":
        benchmark: BenchModuleAccuracy = BenchModuleAccuracy(
            draw_circles=save_circles, draw_center=save_centers
        )
        tester: AccuracyModule = AccuracyModule()
        file_output.write(
            "image,read color,read depth,isInFrame(),getCenter(),get_module_depth(),region_of_interest(),get_module_orientation(),getModuleBounds(),get_module_roll(),exec time (s),total image time (s)\n"
        )
    elif bench_name == "obstacle":
        benchmark: BenchObstacleAccuracy = BenchObstacleAccuracy(plot_obs=plot_boxes)
        tester: AccuracyObstacle = AccuracyObstacle()
        file_output.write(
            "image,read color,read depth,find(),track(),exec time (s),total image time (s)\n"
        )
    elif (
        bench_name == "pylon"
    ):  ## NOTE: pylon algorithm not in use, so benchmark not implemented
        return
    elif bench_name == "text":
        benchmark: BenchTextAccuracy = BenchTextAccuracy(plot_text=plot_boxes)
        tester: AccuracyRussianWord = AccuracyRussianWord()
        file_output.write(
            "image,read color,read depth,detect_russian_word(),exec time (s),total image time (s)\n"
        )
    else:
        raise RuntimeError("Invalid benchmark")

    total_imgs: int = sum(".jpg" in s for s in os.listdir(folder))
    total_algorithms_time: float = 0  # total time to execute the algorithms
    total_time: float = 0  # total time to read in images and execute algorithms
    file_counter: int = 0

    # Iterate through the images
    for root, _, files in os.walk(folder):
        for file in files:
            if file.endswith(".jpg"):
                file_counter += 1  # Track the number of images processed
                crash = False  # Whether reading in the file crashed

                # Attempt to read the file
                filename = os.path.join(root, file)
                depthname = filename[:-14] + "depthImage.npy"

                image = np.array([])
                depth = np.array([])

                file_output.write(filename + ",")

                start_time = time.time()  # take time before reading in images

                try:
                    image = cv2.imread(filename)
                except:
                    file_output.write("False")
                    crash = True
                if image is None:
                    file_output.write("False")
                    crash = True
                file_output.write("True,")

                try:
                    depth = np.load(depthname)
                except:
                    file_output.write("False")
                    crash = True
                if depth is None:
                    file_output.write("False")
                    crash = True
                file_output.write("True,")

                # Run test if image read successfully
                if not crash:  # image read successfully
                    start_exec_time = time.time()
                    crash: bool = benchmark.bench_accuracy(
                        file_output=file_output,
                        tester=tester,
                        image=image,
                        depth=depth,
                        filename=file,
                    )
                    end_time = time.time()

                    # calculate execution and total times
                    algorithms_time = (
                        end_time - start_exec_time
                    )  # time to execute algorithms
                    image_time = (
                        end_time - start_time
                    )  # time to read in images and execute algorithms
                    file_output.write(str(algorithms_time) + ",")
                    file_output.write(str(image_time))
                    total_algorithms_time += algorithms_time
                    total_time += image_time

                file_output.write("\n")

                # std output of file processing
                if not quiet_output:
                    print(
                        "FILE (" + str(file_counter) + "/" + str(total_imgs) + "):",
                        file,
                        "ALGORITHMS_TIME:",
                        "{:.3f}".format(algorithms_time),
                        "TOTAL_IMAGE_TIME:",
                        "{:.3f}".format(image_time),
                        "CRASH:",
                        crash,
                    )

    # Add timing results to output file
    avg_alg_time = total_algorithms_time / total_imgs
    avg_total_time = total_time / total_imgs
    file_output.write("\n\nAvg Algorithms Time (s): " + str(avg_alg_time) + "\n")
    file_output.write("Total Algorithms Time (s): " + str(total_algorithms_time) + "\n")
    file_output.write("\n\nAvg Total Time Per Image (s): " + str(avg_total_time) + "\n")
    file_output.write("Total Time (s): " + str(total_time) + "\n")

    if not quiet_output:
        print("\n\nAvg Algorithms Time (s): " + str(avg_alg_time))
        print("Total Algorithms Time (s): " + str(total_algorithms_time))
        print("\n\nAvg Total Time Per Image (s): " + str(avg_total_time))
        print("Total Time (s): " + str(total_time))

    return


def run_bag_stream(
    bench_name: str,
    filename: str,
    file_output: IOBase,
    quiet_output: bool = False,
    save_circles: bool = False,
    save_centers: bool = False,
    plot_boxes: bool = False,
    save_frames: bool = True,
) -> None:
    """
    Run the .bag file in "real time" through a benchmark.
    NOTE: Since the file is being run as a stream, the number of frames processed
          will depend on the speed of the algorithms being benchmarked.
          As such, drawing functions will result in fewer frames being processed.

    Parameters
    ----------
    bench_name: str
        The name of the benchmark to run.
    file_output: IOBase
        File output stream for results.
    quiet_output: bool
        Whether to silence terminal output.
    save_circles: bool
        For module benchmark. Whether to save images with circles plotted.
    save_centers: bool
        For module benchmark. Whether to save images with center plotted.
    plot_boxes: bool
        For text and obstacle benchmarks. Whether to save images with bounding boxes plotted.
    save_frames: bool
        Whether or not to save frames pulled from the bag file during benchmark.
        NOTE: Saving frames takes time and will thus result in less frames being pulled from the .bag file.

    Returns
    -------
    None
    """
    SAVED_FRAMES_DIR = "saved_frames"
    if not os.path.isdir(SAVED_FRAMES_DIR):
        os.mkdir(SAVED_FRAMES_DIR)

    benchmark = 0  # benchmark runner class
    tester = 0  # benchmark class to run
    if bench_name == "module":
        benchmark: BenchModuleAccuracy = BenchModuleAccuracy(
            draw_circles=save_circles, draw_center=save_centers
        )
        tester: AccuracyModule = AccuracyModule()
        file_output.write(
            "image,isInFrame(),getCenter(),get_module_depth(),region_of_interest(),get_module_orientation(),getModuleBounds(),get_module_roll(),exec time (s)\n"
        )
    elif bench_name == "obstacle":
        benchmark: BenchObstacleAccuracy = BenchObstacleAccuracy(plot_obs=plot_boxes)
        tester: AccuracyObstacle = AccuracyObstacle()
        file_output.write("image,find(),track(),exec time (s)\n")
    elif (
        bench_name == "pylon"
    ):  ## NOTE: pylon algorithm not in use, so benchmark not implemented
        return
    elif bench_name == "text":
        benchmark: BenchTextAccuracy = BenchTextAccuracy(plot_text=plot_boxes)
        tester: AccuracyRussianWord = AccuracyRussianWord()
        file_output.write("image,detect_russian_word(),exec time (s)\n")
    else:
        raise RuntimeError("Invalid benchmark")

    total_time: float = 0  # total time to execute algorithms
    file_counter: int = 0

    # Initialize stream from bag file
    stream: BagFile = BagFile(SCREEN_WIDTH, SCREEN_HEIGHT, FRAME_RATE, filename, REPEAT)

    # Iterate through the stream
    for depth, image in stream:
        file = str(time.time()) + ".jpg"
        file_counter += 1  # Track the number of images processed
        crash = False  # Whether reading in the file crashed
        file_output.write(file + ",")

        # Run test on frame
        start_exec_time = (
            time.time()
        )  ## NOTE: if save_frames is true, time to save the frame is included in timing

        if save_frames:
            cv2.imwrite(os.path.join(SAVED_FRAMES_DIR, file), image)

        crash: bool = benchmark.bench_accuracy(
            file_output=file_output,
            tester=tester,
            image=image,
            depth=depth,
            filename=file,
        )
        end_time = time.time()

        # calculate execution and total times
        algorithms_time = end_time - start_exec_time  # time to execute algorithms
        file_output.write(str(algorithms_time))
        total_time += algorithms_time

        file_output.write("\n")

        # std output of file processing
        if not quiet_output:
            print(
                "FRAME (" + str(file_counter) + "):",
                file,
                "TIME:",
                "{:.3f}".format(algorithms_time),
                "CRASH:",
                crash,
            )

    # Add timing results to output file
    avg_time = total_time / file_counter
    file_output.write("\n\nAvg Time (s): " + str(avg_time) + "\n")
    file_output.write("Total Time (s): " + str(total_time) + "\n")

    if not quiet_output:
        print("\n\nAvg Time (s): " + str(avg_time))
        print("Total Time (s): " + str(total_time))

    return


def run_bag_set(
    bench_name: str,
    filename: str,
    file_output: IOBase,
    folder_name: str = "new_set",
    quiet_output: bool = False,
    save_circles: bool = False,
    save_centers: bool = False,
    plot_boxes: bool = False,
) -> None:
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
    file_output: IOBase
        File output stream for results.
    folder_name: str
        The folder to save the new dataset to, relative to vision_images.
    quiet_output: bool
        Whether to silence terminal output.
    save_circles: bool
        For module benchmark. Whether to save images with circles plotted.
    save_centers: bool
        For module benchmark. Whether to save images with center plotted.
    plot_boxes: bool
        For text and obstacle benchmarks. Whether to save images with bounding boxes plotted.

    Returns
    -------
    None
    """
    REPEAT = False  # Whether to continously run through the bag file (True will cause infinite image generation)
    IMAGE_FOLDER = os.path.join("vision", "vision_images", folder_name)

    if not quiet_output:
        print("CREATING DATASET")

    if not os.path.isdir(IMAGE_FOLDER):
        os.mkdir(IMAGE_FOLDER)

    # Create the data set from the bag file.
    BagFile(SCREEN_WIDTH, SCREEN_HEIGHT, FRAME_RATE, filename, REPEAT).save_as_img(
        IMAGE_FOLDER
    )

    if not quiet_output:
        print("DATASET CREATED")

    # Run the benchmark on the new dataset
    run_set(
        bench_name=bench_name,
        folder=IMAGE_FOLDER,
        file_output=file_output,
        quiet_output=quiet_output,
        save_circles=save_circles,
        save_centers=save_centers,
        plot_boxes=plot_boxes,
    )

    return


def run_bench(
    bench_name: str,
    file_loc: str,
    dataset_bag: bool = False,
    folder_name: str = "new_set",
    quiet_output: bool = False,
    save_circles: bool = False,
    save_centers: bool = False,
    plot_boxes: bool = False,
    save_frames: bool = True,
) -> None:
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
    folder_name: str
        For .bag files as dataset. Name of folder to save new dataset in. Relative to vision_images
    quiet_output: bool
        Whether to silence terminal output.
    save_circles: bool
        For module benchmark. Whether to save images with circles plotted.
    save_centers: bool
        For module benchmark. Whether to save images with center plotted.
    plot_boxes: bool
        For text and obstacle benchmarks. Whether to save images with bounding boxes plotted.
    save_frames: bool
        For .bag files as stream. Whether or not to save frames pulled from the bag file during benchmark.

    Returns
    -------
    None
    """

    # Initialize csv output file
    f = open(
        OUTPUT_FILE, "w"
    )  # will overwrite existing file, backup previous results if needed

    if file_loc[-4:] == ".bag":  # running on bag file
        if dataset_bag:  # run as dataset of images
            run_bag_set(
                bench_name=bench_name,
                filename=file_loc,
                file_output=f,
                folder_name=folder_name,
                quiet_output=quiet_output,
                save_circles=save_circles,
                save_centers=save_centers,
                plot_boxes=plot_boxes,
            )
        else:  # run as image stream
            run_bag_stream(
                bench_name=bench_name,
                filename=file_loc,
                file_output=f,
                quiet_output=quiet_output,
                save_circles=save_circles,
                save_centers=save_centers,
                plot_boxes=plot_boxes,
                save_frames=save_frames,
            )

    else:  # running on image directory
        run_set(
            bench_name=bench_name,
            folder=file_loc,
            file_output=f,
            quiet_output=quiet_output,
            save_circles=save_circles,
            save_centers=save_centers,
            plot_boxes=plot_boxes,
        )

    f.close()
    return


if __name__ == "__main__":
    """
    Run a specified benchmark on a dataset or .bag file.

    Command Line Arguments
    ----------------------
    -b, --bench_name {benchmark_name}
        Required. Name of benchmark to run.
    -f, --folder {foldername}
        Required. Folder to run accuracy benchmarks on.
    -q, --quiet
        produce no output while running
    -d, --dataset_bag
        For use with .bag files. Enables creation of and iteration through data set of images.
    -n, --dataset_name {name}
        Name of new dataset if parsing bag as dataset. Defaults to new_set if not specified.
    -c, --save_circles
        Save images with circles when the module is in frame.
    -e, --save_centers
        Save images with centers when the module is in frame.
    -p, --plot_boxes
        Save images with bounding boxes plotted (for obstacles or text).
    -s, --skip_save_frame
        For use with .bag files as streams. Disables saving frames pulled from video.
    """
    import argparse

    parser = argparse.ArgumentParser(
        description="Must specify benchmark name and file location."
    )

    ## handle argument parsing ##

    # Settings
    parser.add_argument(
        "-b",
        "--bench_name",
        type=str,
        help="Name of the benchmark to run. Can be module, obstacle, pylon, or text. Required Argument.",
    )
    parser.add_argument(
        "-f",
        "--file_location",
        type=str,
        help="Location of the .bag file to run or the folder of the data set to run. Required Argument.",
    )
    parser.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Output no file information while running",
    )

    # .bag file settings
    parser.add_argument(
        "-d",
        "--dataset_bag",
        action="store_true",
        help="For use with .bag files. Enables creation of and iteration through data set of images.",
    )
    parser.add_argument(
        "-n",
        "--dataset_name",
        type=str,
        help="Name of new dataset if parsing bag as dataset. Defaults to new_set if not specified.",
    )
    parser.add_argument(
        "-s",
        "--skip_save_frame",
        action="store_true",
        help="For use with .bag files as streams. Disables saving frames pulled from video.",
    )

    # module benchmark settings
    parser.add_argument(
        "-c",
        "--save_circles",
        action="store_true",
        help="Save images with circles when the module is in frame.",
    )
    parser.add_argument(
        "-e",
        "--save_centers",
        action="store_true",
        help="Save images with centers when the module is in frame.",
    )

    # Text and Obstacle benchmark settings
    parser.add_argument(
        "-p",
        "--plot_boxes",
        action="store_true",
        help="Save images with bounding boxes plotted (for obstacles or text).",
    )

    args = parser.parse_args()

    # no benchmark name specified, cannot continue
    if not args.bench_name:
        raise RuntimeError("No benchmark specified.")

    # no file location specified, cannot continue
    if not args.file_location:
        raise RuntimeError("No file location specified.")

    folder_name = "new_set"
    if args.dataset_name:
        folder_name = args.dataset_name
    save_frames = not args.skip_save_frame

    run_bench(
        bench_name=args.bench_name,
        file_loc=args.file_location,
        dataset_bag=args.dataset_bag,
        folder_name=folder_name,
        quiet_output=args.quiet,
        save_circles=args.save_circles,
        save_centers=args.save_centers,
        plot_boxes=args.plot_boxes,
        save_frames=save_frames,
    )
