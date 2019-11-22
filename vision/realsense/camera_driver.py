"""
This program was written to test/be an example for the camera child classes

To avoid confusion in the example, only uncomment one camera child use at a time

To use the realsense, a realsense must be plugged in

To use the bag reader, run the program from the terminal
with "python camera_driver.py -i (bag file name).bag", and the bag
file must be in the same directory as this program

For the program to run, template.py, realsense.py, and bag_file.py
must be in the same directory, or you need to manually change their location
in the import section
"""

import os.path
import argparse
import realsense
import bag_file
# import sim_camera ---> unnecessary of now

#######################################################
#  Testing the Realsense class                        #
#######################################################

# camera = realsense.Realsense(640, 480, 30)
# camera.display_in_window()

#######################################################
#  Testing the BagFile class                          #
#######################################################

# # Create object for parsing command-line options
# parser = argparse.ArgumentParser(description="Read recorded bag file and display depth and color streams.\
#                                  Remember to change the stream resolution, fps and format to match the recorded.\
#                                  To read a .bag file, type \"python read_bag.py --input bag_name.bag\"")
# # Add argument which takes path to a bag file as an input
# parser.add_argument("-i", "--input", type=str, help="Path to the bag file")
# # Parse the command line arguments to an object
# args = parser.parse_args()
# # Safety if no parameter have been given
# if not args.input:
#     raise FileNotFoundError("No input parameter has been given. For help type --help")
# # Check if the given file have bag extension
# if os.path.splitext(args.input)[1] != ".bag":
#     raise ValueError("The given filename is not of correct file format, only .bag accepted")
#
# bag_reader = bag_file.BagFile(1280, 720, 30, args.input)
#
# bag_reader.display_in_window()

#######################################################
#  Testing the SimCamera class                        #
#######################################################

