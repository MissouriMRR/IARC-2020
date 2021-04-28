"""
Tool to capture scene (analogous to color images from realsense)
and depth images from airsim

A commented snippet of code is also included to demonstrate how to
translate the images into a numpy array for further processing

To capture/save images, start and run the airsim. Then, navigate to
the location of this program in terminal, and run using
"python capture_airsim_image.py". Enter q to capture an image, or e to exit.
"""
import datetime
import pickle
import cv2
import numpy as np
import airsim

client = airsim.MultirotorClient()

while True:  # runs as long as the simulator is running, ideally
    key = input("Enter q to capture scene and depth images, or e to exit. ")
    if key == "q":
        ## TODO get as numpy array
        # reportedly this is an png returned, not sure how that works
        sceneCameraImage = client.simGetImage("0", airsim.ImageType.Scene)
        depthCameraImage = client.simGetImage("3", airsim.ImageType.Scene)

        time = str(datetime.datetime.now()).replace(" ", "_").replace(":", ".")

        cv2.imwrite(f"{time}-colorImage.jpg", sceneCameraImage)

        with open(f"{time}-depthImage.npy", "wb") as file:
            np.save(file, depthCameraImage)

    if key == "e":
        break
