import cv2
import numpy as np
import argparse
import imutils

#CLASSIFY
'''
cap = cv2.VideoCapture(0)

while True:
    _, frame = cap.read()
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    #Red Color
    lowRed = np.array([125, 70, 70])#161, 151, 84
    highRed = np.array([225,255,255])#179,255,255
    redMask = cv2.inRange(hsv_frame, lowRed, highRed)
    red = cv2.bitwise_and(frame, frame, mask=redMask)

    #White Color
    lowWhite = np.array([0,0,0])
    highWhite = np.array([10, 255, 255])
    whiteMask = cv2.inRange(hsv_frame, lowWhite, highWhite)
    white = cv2.bitwise_and(frame, frame, mask=whiteMask)

    combined = cv2.bitwise_and(red, white)



    cv2.imshow("Frame", frame)
    cv2.imshow("Detect",combined)

    key = cv2.waitKey(1)
    if key == 27:
        break
'''
img = cv2.imread('IARC-2020/vision/resources/bshapes.png')

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

combined = cv2.bitwise_or(white, red)


cv2.imshow('red', combined)
cv2.waitKey(0)

thresh = cv2.Canny(combined, 60, 120)

pic = thresh

#Corners

corners = cv2.goodFeaturesToTrack(pic, 100, 0.01, 10)
corners = np.int0(corners)

for corner in corners:
    x,y = corner.ravel()
    cv2.circle(pic,(x,y),3,255,-1)

cv2.imshow('Corner',pic)
cv2.waitKey(0)
cv2.destroyAllWindows()
