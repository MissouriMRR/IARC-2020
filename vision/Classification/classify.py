import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while True:
    _, frame = cap.read()
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    #Red Color
    lowRed = np.array([0, 50, 25])#161, 151, 84
    highRed = np.array([10,255,255])#179,255,255
    redMask = cv2.inRange(hsv_frame, lowRed, highRed)
    red = cv2.bitwise_and(frame, frame, mask=redMask)

    #blue Color
    lowBlue = np.array([94,80,2])
    highBlue = np.array([126, 255, 255])
    blueMask = cv2.inRange(hsv_frame, lowBlue, highBlue)
    blue = cv2.bitwise_and(frame, frame, mask=blueMask)

    #Green Color
    lowGreen = np.array([25,52,72])
    highGreen = np.array([102,255, 255])
    greenMask = cv2.inRange(hsv_frame, lowGreen, highGreen)
    green = cv2.bitwise_and(frame, frame, mask=greenMask)

    #Every color except white
    low = np.array([0,42,0])
    high = np.array([179, 255, 255])
    mask = cv2.inRange(hsv_frame, low, high)
    result = cv2.bitwise_and(frame, frame, mask = mask)

    cv2.imshow("Frame", frame)
    cv2.imshow("red",red )
    cv2.imshow("blue", blue)
    cv2.imshow("green", green)

    key = cv2.waitKey(1)
    if key == 27:
        break