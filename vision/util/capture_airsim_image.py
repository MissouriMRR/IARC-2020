"""
Tool to capture scene (analogous to color images from realsense)
and depth images from airsim

A commented snippet of code is also included to demonstrate how to
translate the images into a numpy array for further processing

To capture/save images, start and run the airsim. Then, navigate to
the location of this program in terminal, and run using
"python capture_airsim_image.py". Enter q to capture an image, or e to exit.
"""
import airsim
import cv2
import numpy as np

client = airsim.MultirotorClient()

while True:  # runs as long as the simulator is running, ideally
    key = input("Enter q to capture scene and depth images, or e to exit. ")
    if key == "q":
        sceneCameraImage = client.simGetImage("0", airsim.ImageType.Scene)  # reportedly this is an png returned, not sure how that works
        depthCameraImage = client.simGetImage("3", airsim.ImageType.Scene)
        f = open('sceneFrame.png', 'wb')
        f.write(sceneCameraImage)
        f.close()
        g = open('depthFrame.png', 'wb')
        g.write(depthCameraImage)
        g.close()

    # get numpy array
    # img1d = np.fromstring(cameraImage.image_data_uint8, dtype=np.uint8)

    if key == "e":
        break

