import cv2
import numpy as np

def shapeDetection(image):
    gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    gray = np.float32(gray)

    corners = cv2.goodFeaturesToTrack(gray, 100, 0.01, 10)
    corners = np.int0(corners)

    for corner in corners:
        x,y = corner.ravel()

    return corners

if __name__ == '__main__':
    img = cv2.imread('IARC-2020/vision/ShapeDetection/resources/pylon.png')
