import cv2
import numpy as np

def classifier(img):
    # img = cv2.imread('IARC-2020/vision/pylon/resources/pylon.png')

    # It converts the BGR color space of image to HSV color space
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)

    # Threshold of blue in HSV space
    lowRed = np.array([125, 75, 75])
    highRed = np.array([225,255,255])
    # preparing the mask to overlay
    redMask = cv2.inRange(hsv, lowRed, highRed)
    # The black region in the mask has the value of 0,
    # so when multiplied with original image removes all non-blue regions
    red = cv2.bitwise_and(img, img, mask=redMask)

    #Repeat with white mask
    lowWhite = np.array([0,0,0])
    highWhite = np.array([1,255,255])
    whiteMask = cv2.inRange(hsv, lowWhite, highWhite)
    white = cv2.bitwise_and(img, img, mask=whiteMask)

    if __name__ == '__main__':
        combined = cv2.bitwise_or(white, red)
        edges_high_thresh = cv2.Canny(img, 60, 120)
        cv2.imshow('Edges',edges_high_thresh)
        cv2.imshow('combined', combined)
        cv2.waitKey(0)

classifier(cv2.imread('IARC-2020/vision/pylon/resources/pylon.png'))