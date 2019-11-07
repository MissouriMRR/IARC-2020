
"""
Loads and displays a video.
"""

# Importing OpenCV
import cv2
import numpy as np
 
# Create a VideoCapture object and read from input file
# If the input is the camera, pass 0 instead of the video file name
cap = cv2.VideoCapture(0)
 
# Check if camera opened successfully
if (cap.isOpened()== False): 
  print("Error opening video stream or file")
 
fgbg = cv2.createBackgroundSubtractorMOG2(
    history=10,
    varThreshold=2,
    detectShadows=False)

# Read the video
while(cap.isOpened()):
  # Capture frame-by-frame
  ret, frame = cap.read()
  if ret == True:
 
    # Converting the image to grayscale.
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    
    # Extract the foreground
    edges_foreground = cv2.bilateralFilter(gray, 9, 75, 75)
    foreground = fgbg.apply(edges_foreground)
    
    # Smooth out to get the moving area
    kernel = np.ones((50,50),np.uint8)
    foreground = cv2.morphologyEx(foreground, cv2.MORPH_CLOSE, kernel)

    # Applying static edge extraction
    edges_foreground = cv2.bilateralFilter(gray, 9, 75, 75)
    edges_filtered = cv2.Canny(edges_foreground, 60, 120)

    # Using the Canny filter with different parameters
    edges_high_thresh = cv2.Canny(gray, 60, 120)

    # Crop off the edges out of the moving area
    cropped = (foreground // 255) * edges_high_thresh

    # Stacking the images to print them together for comparison
    #cropped is registered by motion
    images = np.hstack((edges_high_thresh, cropped))

    # Display the resulting frame
    cv2.imshow('Frame', images)

    # Press Q on keyboard to  exit
    if cv2.waitKey(25) & 0xFF == ord('q'):
      break
 
  # Break the loop
  else: 
    break
 
# When everything done, release the video capture object
cap.release()
 
# Closes all the frames
cv2.destroyAllWindows()