"""
This program will align and stream color and depth images to a window for the user.
For this program to run correctly, the realsense must be plugged in to the computer,
and must not be currently streaming in another program/software.
"""

# First import the library
import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2

if __name__ == '__main__':
    #Initialize resolution and framerate constants
    RESOLUTION_WIDTH = 640
    RESOLUTION_HEIGHT = 480
    FRAMERATE = 30

    #Initalize clipping constants
    CLIPPING = False
    clipping_distance_in_meters = 4

    #Initialize serial number constant-- if empty, no serial number is specified
    SERIAL_NUMBER = ""

    # Create a pipeline
    pipeline = rs.pipeline()

    # Create a config and configure the pipeline to stream
    # different resolutions of color and depth streams (hypothetically)
    config = rs.config()

    #a unique serial number for a camera, enables config to get data from a specific camera
    if SERIAL_NUMBER:
        config.enable_device(SERIAL_NUMBER)

    config.enable_stream(rs.stream.depth, RESOLUTION_WIDTH, RESOLUTION_HEIGHT, rs.format.z16, FRAMERATE)
    config.enable_stream(rs.stream.color, RESOLUTION_WIDTH, RESOLUTION_HEIGHT, rs.format.bgr8, FRAMERATE)

    # Start streaming
    profile = pipeline.start(config)

    # Getting the depth sensor's depth scale (see rs-align example for explanation)
    depth_sensor = profile.get_device().first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()

    # We will be removing the background of objects more than
    #  clipping_distance_in_meters meters away
    if CLIPPING:
        clipping_distance = clipping_distance_in_meters / depth_scale

    # Create an align object
    # rs.align allows us to perform alignment of depth frames to others frames
    # The "align_to" is the stream type to which we plan to align depth frames.
    align_to = rs.stream.color
    align = rs.align(align_to)

    # Streaming loop
    while True:
        # Get frameset of color and depth
        frames = pipeline.wait_for_frames()
        # frames.get_depth_frame() is a 640x360 depth image

        # Align the depth frame to color frame
        aligned_frames = align.process(frames)

        # Get aligned frames
        aligned_depth_frame = aligned_frames.get_depth_frame() # aligned_depth_frame is a 640x480 depth image
        color_frame = aligned_frames.get_color_frame()

        # Validate that both frames are valid
        if not aligned_depth_frame or not color_frame:
            continue

        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Remove background - Set pixels further than clipping_distance to grey
        grey_color = 153
        depth_image_3d = np.dstack((depth_image,depth_image,depth_image)) #depth image is 1 channel, color is 3 channels
        if CLIPPING:
            bg_removed = np.where((depth_image_3d > clipping_distance) | (depth_image_3d <= 0), grey_color, color_image)
        else:
            bg_removed = np.where((depth_image_3d <= 0), grey_color, color_image)

        # Render images
        depth_colormap = cv2.applyColorMap(cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET)
        images = np.hstack((bg_removed, depth_colormap))
        cv2.namedWindow('Depth/Color Stream', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Depth/Color Stream', images)
        key = cv2.waitKey(1)
        # Press esc or 'q' to close the image window
        if key == ord('q') or key == 27 or cv2.getWindowProperty('Depth/Color Stream', 0) == -1:
            cv2.destroyAllWindows()
            break

    pipeline.stop()
