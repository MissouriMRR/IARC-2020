import cv2
import numpy as np

# detect_red detects all pixels that fall in a certain range in an image
# then outputs the original image and detected mask
def detect_red(image):
    # Convert the image from BGR to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Set the lower and upper color limits
    lower_red = np.array([50, 150, 25])
    upper_red = np.array([255, 255, 120])
    # Red_mask picks out any pixel between the lower and upper limits
    # and replaces them with white.  Everything else is replaced with black
    red_mask = cv2.inRange(hsv, lower_red, upper_red)

    # Run through each pixel in the mask.  If one is white, then
    # we detected part of the pylon
    pylon = False
    for x in range(0, red_mask.shape[0]):
        for y in range(0, red_mask.shape[1]):
            if red_mask[x, y] != 0:
                pylon = True

    return pylon

image = cv2.imread("sim_pylon2.png")
print(detect_red(image))