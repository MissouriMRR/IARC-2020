import cv2
import numpy as np
import vision.blob.constants as constants
import os

def configure_params():
    params = cv2.SimpleBlobDetector_Params()

    params.filterByArea = True
    params.maxArea = constants.MAX_AREA

    return params

def find_blobs(image):
    image = cv2.imread(image)
    print('Starting...')

    params = configure_params()
    blob_detector = cv2.SimpleBlobDetector_create(params)

    keypoints = blob_detector.detect(image)
    print(keypoints)
    im_with_keypoints = cv2.drawKeypoints(image, keypoints, outImage=np.array([]), color=(0, 0, 255), flags=cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)

    cv2.imshow("Keypoints", im_with_keypoints)
    cv2.waitKey(0)
    return


for img in os.listdir('samples'):
    find_blobs('samples/' + os.fsdecode(img))