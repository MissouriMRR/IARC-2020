"""
Called to save a depth and color frame with timed labels
"""
import datetime
import pickle
import os
import cv2, numpy as np


def save_camera_frame(
    depth_frame: np.ndarray, color_frame: np.ndarray, path: str = ""
) -> None:
    """
    Saves depth frame and color frame, named according to the time it was taken.

    Parameters
    ----------
    depth_frame: numpy array
        Depth image from the moment that c was pressed
    color_frame: numpy array
        Color image from the moment that c was pressed
    path: str
        The path to save the frame to.

    Returns
    -------
    None
    """
    time = str(datetime.datetime.now()).replace(" ", "_").replace(":", ".")

    cv2.imwrite(os.path.join(path, f"{time}-colorImage.jpg"), color_frame)

    with open(os.path.join(path, f"{time}-depthImage.npy"), "wb") as file:
        np.save(file, depth_frame)
