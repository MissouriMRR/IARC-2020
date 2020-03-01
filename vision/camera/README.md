# Camera Modules
All camera modules have a generic interface so they can be swapped out easily.

## Example Code

The following are examples of how to use the camera child classes. As always, make sure to either change file import paths,
or to download everything into the same file.

### Reading Images

#### .jpg/.png

These are standard image formats, used for color images.

```python
import cv2

## Saving
cv2.imwrite("filename", ndarray) -> bool

## Reading
cv2.imread("filename") -> ndarray
```

#### .npy

This is a numpy array file, used for depth images.

```python
## Saving .npy
with open('filename.npy', 'wb') as file:
    pickle.dump(file, ndarray)

## Reading .npy
with open('filename.npy', 'rb') as file:
    ndarray = numpy.load(file)
```

#### .bag

This is a rosbag file, used for color+depth videos.
Use the bag_file reader, follow instructions for that class below.

### Realsense Example

If only one realsense is plugged in, the code will run normally. If you are using more than one camera, make sure to specify the serial number.

```Python
#######################################################
#  Testing the Realsense class                        #
#######################################################

import realsense

camera = realsense.Realsense(640, 480, 30)
camera.display_in_window()
```

### Pre-recorded BAG Example

To use the bag reader, run the program from the terminal
with "python camera_driver.py -i (bag file name).bag", and the bag
file must be in the same directory as this program.

```Python
#######################################################
#  Testing the BagFile class                          #
#######################################################

import bag_file

# Create object for parsing command-line options
parser = argparse.ArgumentParser(description="Read recorded bag file and display depth and color streams.\
                                  Remember to change the stream resolution, fps and format to match the recorded.\
                                  To read a .bag file, type \"python read_bag.py --input bag_name.bag\"")
# Add argument which takes path to a bag file as an input
parser.add_argument("-i", "--input", type=str, help="Path to the bag file")
# Parse the command line arguments to an object
args = parser.parse_args()
# Safety if no parameter have been given
if not args.input:
     raise FileNotFoundError("No input parameter has been given. For help type --help")
# Check if the given file have bag extension
if os.path.splitext(args.input)[1] != ".bag":
     raise ValueError("The given filename is not of correct file format, only .bag accepted")

bag_reader = bag_file.BagFile(1280, 720, 30, args.input)

bag_reader.display_in_window()
```

### Sim Camera Example

To use the sim camera, run the program from the terminal
with "python camera_driver.py". The airsim must also be running
for the sim camera class to work.

[Airsim Image API](https://github.com/microsoft/AirSim/blob/master/docs/image_apis.md#what-does-pixel-values-mean-in-different-image-types)

```Python
#######################################################
#  Testing the Sim Camera                             #
#######################################################

import sim_camera

sim_cam = sim_camera.SimCamera()
sim_cam.display_in_window()
```
