"""
This program will save a color frame as a JPG, the depth frame as a JPG,
and the depth scale in a .txt file for use in image processing.
"""


# First import the library
import pyrealsense2 as rs
# Import Numpy for easy array manipulation
import numpy as np
# Import OpenCV for easy image rendering
import cv2
# Import datetime for filename
import datetime

# Create a pipeline
pipeline = rs.pipeline()

# Create a config and configure the pipeline to stream
# different resolutions of color and depth streams
config = rs.config()
#config.enable_device("846112073537") #a (hopefully unique) serial number for a camera, enables config to get data from a specific camera
#declare them as constants at the top of the program later
#we can create a new 'config' for each camera?
#I think it is, actually, unique, because most serial numbers are, and no data is taken if the number is changed
config.enable_stream(rs.stream.depth, 640, 480, rs.format.z16, 30)
config.enable_stream(rs.stream.color, 640, 480, rs.format.bgr8, 30)

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


# Get frameset of color and depth
frames = pipeline.wait_for_frames()
# frames.get_depth_frame() is a 640x360 depth image

# Align the depth frame to color frame
aligned_frames = align.process(frames)

# Get aligned frames
aligned_depth_frame = aligned_frames.get_depth_frame() # aligned_depth_frame is a 640x480 depth image
color_frame = aligned_frames.get_color_frame()

depth_image = np.asanyarray(aligned_depth_frame.get_data())
color_image = np.asanyarray(color_frame.get_data())

time = str(datetime.datetime.now()).replace(' ', '_').replace(':', '.')
cv2.imwrite(f"{time}-colorImage.jpg", color_image)
cv2.imwrite(f"{time}-depthImage.jpg", depth_image)
with open(f"{time}-depthScale.txt", 'w') as file:
    file.write(str(depth_scale))

pipeline.stop()
