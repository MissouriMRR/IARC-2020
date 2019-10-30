"""
This program will save a color frame as a JPG, the depth frame as a JPG,
and the depth scale in a .txt file for use in image processing. The realsense camera must be
plugged into the computer, and must not be currently streaming for the program to work.

The files are all saved in the same directory as the program, and are named using the current
date and time at which the frames were taken, followed by either "-depthImage", "-colorImage",
or "-depthScale" accordingly.
"""
import datetime

import cv2
import numpy as np
import pyrealsense2 as rs


def save_frame_on_press(width, height, framerate, serial_no=None):
    """
    Enable the realsense camera and upon q/ESC press capture image.

    Parameters
    ----------
    width: int
        Camera res width.
    height: int
        Camera res height.
    framerate: int
        Images captures per second.
    serial_no: str, default=None
        Serial number of camera if want specific one.

    Effects
    -------
    Saves color and depth images w/ date as title in current directory.
    """
    # Create a pipeline
    pipeline = rs.pipeline()

    # Create a config and configure the pipeline to stream
    # different resolutions of color and depth streams (hypothetically)
    config = rs.config()

    #a unique serial number for a camera, enables config to get data from a specific camera
    if serial_no:
        config.enable_device(serial_no)

    config.enable_stream(rs.stream.depth, width, height, rs.format.z16, framerate)
    config.enable_stream(rs.stream.color, width, height, rs.format.bgr8, framerate)

    # Start streaming
    profile = pipeline.start(config)

    # Getting the depth sensor's depth scale (see rs-align example for explanation)
    depth_sensor = profile.get_device().first_depth_sensor()
    depth_scale = depth_sensor.get_depth_scale()

    # Create an align object
    # rs.align allows us to perform alignment of depth frames to others frames
    # The "align_to" is the stream type to which we plan to align depth frames.
    align_to = rs.stream.color
    align = rs.align(align_to)

    while True:
        # Get frameset of color and depth
        frames = pipeline.wait_for_frames()
        # frames.get_depth_frame() is a 640x360 depth image

        # Align the depth frame to color frame
        aligned_frames = align.process(frames)

        # Get aligned frames
        # aligned_depth_frame is a 640x480 depth image
        aligned_depth_frame = aligned_frames.get_depth_frame()
        color_frame = aligned_frames.get_color_frame()

        # Validate that both frames are valid
        if not aligned_depth_frame or not color_frame:
            continue

        depth_image = np.asanyarray(aligned_depth_frame.get_data())
        color_image = np.asanyarray(color_frame.get_data())

        # Remove background - Set pixels further than clipping_distance to grey
        grey_color = 153
        depth_image_3d = np.dstack((depth_image, depth_image, depth_image))
        bg_removed = np.where((depth_image_3d <= 0), grey_color, color_image)

        # Render images
        depth_colormap = cv2.applyColorMap(
            cv2.convertScaleAbs(depth_image, alpha=0.03),
            cv2.COLORMAP_JET)
        images = np.hstack((bg_removed, depth_colormap))

        cv2.namedWindow('Depth/Color Stream', cv2.WINDOW_AUTOSIZE)
        cv2.imshow('Depth/Color Stream', images)
        key = cv2.waitKey(1)

        # Press the X button on the window to close the window
        if cv2.getWindowProperty('Depth/Color Stream', 0) == -1:
            cv2.destroyAllWindows()
            break

        # Press esc (27) or 'q' to take the pictures and close the window
        if key == ord('q') or key == 27:
            time = str(datetime.datetime.now()).replace(' ', '_').replace(':', '.')

            cv2.imwrite(f"{time}-colorImage.jpg", color_image)
            cv2.imwrite(f"{time}-depthImage.jpg", depth_image)
            with open(f"{time}-depthScale.txt", 'w') as file:
                file.write(str(depth_scale))

            cv2.destroyAllWindows()
            break

    pipeline.stop()


if __name__ == '__main__':
    save_frame_on_press(width=640, height=480, framerate=30)
