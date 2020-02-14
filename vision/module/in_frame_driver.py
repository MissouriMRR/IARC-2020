"""
Driver file to test in_frame with various test images

To run in_frame_driver, use
"python in_frame_driver.py -i (image name).(image file extension)"

Also note that in_frame, in_frame_driver, and the desired test image
must be in the same file location
"""
from in_frame import ModuleInFrame
import numpy as np
import cv2
import argparse

# # Create object for parsing command-line options
parser = argparse.ArgumentParser(description="Read image file and display depth and test for ModuleInFrame.\
                                 To read an image file, type \"python in_frame_driver.py --i (image name).(image extension)\"")
# # Add argument which takes path to a bag file as an input
parser.add_argument("-i", "--input", type=str, help="Path to the image file")
# # Parse the command line arguments to an object
args = parser.parse_args()
# # Safety if no parameter have been given
if not args.input:
    raise FileNotFoundError("No input parameter has been given. For help type --help")

image = cv2.imread(args.input)
npImage = np.asarray(image)

print("Module in frame: " + str(ModuleInFrame(npImage)))

