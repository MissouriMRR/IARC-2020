"""
Test program from the examples in the RealSense repo (at
https://github.com/IntelRealSense/librealsense/tree/master/wrappers/python/examples)
to read .bag files into a python program

For the program to work, you must enter the correct resolution width, height,
framerate, depth stream type, and color stream type
"""


# First import library
import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2
# Import argparse for command-line options
import argparse
# Import os.path for file path manipulation
import os.path

def read_from_bag(width, height, framerate, depth_type, color_type):
    # Create object for parsing command-line options
    parser = argparse.ArgumentParser(description="Read recorded bag file and display depth and color streams in\
                                    Remember to change the stream resolution, fps and format to match the recorded.")
    # Add argument which takes path to a bag file as an input
    parser.add_argument("-i", "--input", type=str, help="Path to the bag file")
    # Parse the command line arguments to an object
    args = parser.parse_args()
    # Safety if no parameter have been given
    if not args.input:
        print("No input parameter has been given.")
        print("For help type --help")
        exit()
    # Check if the given file have bag extension
    if os.path.splitext(args.input)[1] != ".bag":
        print("The given file is not of correct file format.")
        print("Only .bag files are accepted")
        exit()

    # Create pipeline
    pipeline = rs.pipeline()

    # Create a config object
    config = rs.config()
    # Tell config that we will use a recorded device from file to be used by the pipeline through playback.
    rs.config.enable_device_from_file(config, args.input)
    # Configure the pipeline to stream the depth/color streams

    #---------------format the string to use the depth/color type parameters--------------
    config.enable_stream(rs.stream.depth, width, height, rs.format.z16, framerate)
    config.enable_stream(rs.stream.color, width, height, rs.format.rgb8, framerate)
    #-----------------------------------------------------------------------------------

    # Start streaming from file
    pipeline.start(config)

    #----------------------------------------------
    # Create opencv window to render image in
    #cv2.namedWindow("Depth Stream", cv2.WINDOW_AUTOSIZE)
    #-----------------------------------------------------

    # Create colorizer object
    colorizer = rs.colorizer()

    # Create an align object
    # rs.align allows us to perform alignment of depth frames to others frames
    # The "align_to" is the stream type to which we plan to align depth frames.
    align_to = rs.stream.color
    align = rs.align(align_to)

    # Streaming loop
    while True:
        # Get frameset of depth
        frames = pipeline.wait_for_frames()

        # Align the depth frame to color frame
        aligned_frames = align.process(frames)

        # Get aligned frames
        aligned_depth_frame = aligned_frames.get_depth_frame()  # aligned_depth_frame is a 640x480 depth image
        color_frame = aligned_frames.get_color_frame()

        # Validate that both frames are valid
        if not aligned_depth_frame or not color_frame:
            continue

        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Remove background - Set pixels further than clipping_distance to grey
        grey_color = 153
        depth_image_3d = np.dstack((depth_image, depth_image, depth_image))  # depth image is 1 channel, color is 3 channels
        bg_removed = np.where((depth_image_3d <= 0), grey_color, color_image)

        #render depth/color images
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        images = np.hstack((bg_removed, depth_colormap))
        cv2.namedWindow('Depth/Color Stream', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Depth/Color Stream', images)
        key = cv2.waitKey(1)
        # if pressed 'q' or escape (27) exit program
        if key == ord('q') or key == 27 or cv2.getWindowProperty("Depth/Color Stream", 0) == -1:
            cv2.destroyAllWindows()
            break


if __name__ == '__main__':
    read_from_bag(1280, 720, 30, 'z16', 'rgb8')


#ISSUE: The colors are shifted, I think the issue comes from the fact that the .bag was recorded in rgb8,
#and, I think, numpy uses bgr8 by default-- probably and easy fix, but I don't know what it is yet