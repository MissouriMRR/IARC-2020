"""
Called to save a depth and color frame with timed labels
"""
import datetime
import pickle
import cv2, numpy as np


def save_camera_frame(depth_frame, color_frame):
    """
    Saves depth frame and color frame, named according to the time it was taken

    Parameters
    ---------------
    depth_frame: numpy array
        depth image from the moment that c was pressed
    color_frame: numpy array
        color image from the moment that c was pressed
    """
    time = str(datetime.datetime.now()).replace(' ', '_').replace(':', '.')

    cv2.imwrite(f"{time}-colorImage.jpg", color_frame)

    with open(f"{time}-depthImage.npy", 'wb') as file:
        np.save(file, depth_frame)
