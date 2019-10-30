"""
Test program from the examples in the RealSense repo (at
https://github.com/IntelRealSense/librealsense/tree/master/wrappers/python/examples)
to read .bag files into a python program

For the program to work, you must enter the correct resolution width, height,
frame rate, depth stream type, and color stream type

To use the program, navigate to where it is stored, and type
"python read_bag.py -i bag_file_name.bag"
or
"python read_bag.py --input bag_file_name.bag"
"""
import argparse
import os.path

import cv2
import numpy as np
import pyrealsense2 as rs


class ReadBag:
    def __init__(self, arg_input, screen_width=1280, screen_height=720, frame_rate=30):
        self.input = arg_input
        self.width = screen_width
        self.height = screen_height
        self.framerate = frame_rate
        self.pipeline = rs.pipeline()

        # Create a config object
        config = rs.config()
        # Tell config that we will use a recorded device from file
        # to be used by the pipeline through playback.
        rs.config.enable_device_from_file(config, args.input)
        # Configure the pipeline to stream the depth/color streams

        # ---------------format the string to use the depth/color type parameters--------------
        config.enable_stream(rs.stream.depth, self.width, self.height, rs.format.z16, self.framerate)
        config.enable_stream(rs.stream.color, self.width, self.height, rs.format.rgb8, self.framerate)
        # -----------------------------------------------------------------------------------

        # Start streaming from file
        self.pipeline.start(config)

    def __iter__(self):
        while True:
            # returns the next color/depth frame
            frames = self.pipeline.wait_for_frames()

            # Align the depth frame to color frame
            aligned_frames = align.process(frames)

            # Get aligned frames
            # aligned_depth_frame is a 640x480 depth image
            aligned_depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()

            depth_image = np.asanyarray(aligned_depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            color_image = color_image[:, :, ::-1]  # shifts colors back to normal

            yield depth_image, color_image



if __name__ == '__main__':
    WIDTH = 1280
    HEIGHT = 720
    FRAMES = 30

    # Create object for parsing command-line options
    parser = argparse.ArgumentParser(description="Read recorded bag file and display depth and color streams.\
                                     Remember to change the stream resolution, fps and format to match the recorded.\
                                     To read a .bag file, type \"python read_bag.py --input bag_name.bag\"")
    # Add argument which takes path to a bag file as an input
    parser.add_argument("-i", "--input", type=str, help="Path to the bag file")
    # Parse the command line arguments to an object
    args = parser.parse_args()
    # Safety if no parameter have been given
    if not args.input:
        raise FileNotFoundError("No input parameter has been given. For help type --help")
    # Check if the given file have bag extension
    if os.path.splitext(args.input)[1] != ".bag":
        print("The given file is not of correct file format.")
        print("Only .bag files are accepted")
        exit()

    align_to = rs.stream.color
    align = rs.align(align_to)

    # self is passed as the first argument automatically, for both
    bagReader = ReadBag(args.input, WIDTH, HEIGHT, FRAMES)
    for depth_image, color_image in bagReader:
        # Remove background - Set pixels further than clipping_distance to grey
        grey_color = 153
        depth_image_3d = np.dstack((depth_image, depth_image, depth_image))
        bg_removed = np.where((depth_image_3d <= 0), grey_color, color_image)

        # render depth/color images
        depth_colormap = cv2.applyColorMap(
            cv2.convertScaleAbs(depth_image, alpha=0.03),
            cv2.COLORMAP_JET)
        images = np.hstack((bg_removed, depth_colormap))
        cv2.namedWindow('Depth/Color Stream', cv2.WINDOW_NORMAL)
        cv2.resizeWindow('Depth/Color Stream', (WIDTH, int(HEIGHT / 2)))
        cv2.imshow('Depth/Color Stream', images)
        key = cv2.waitKey(1)
        # if pressed 'q' or escape (27) exit program
        if key == ord('q') or key == 27 or cv2.getWindowProperty("Depth/Color Stream", 0) == -1:
            cv2.destroyAllWindows()
            break
