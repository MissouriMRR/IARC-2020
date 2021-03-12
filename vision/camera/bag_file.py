"""
The BagFile class is a child class of the camera, designed to be used for pre-recorded .bag files
"""

import os
import sys

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import cv2
import numpy as np
import pyrealsense2 as rs

try:
    from vision.camera.template import Camera
except ImportError:
    from template import Camera
try:
    from vision.common.take_picture import save_camera_frame
except ImportError:
    from common.take_picture import save_camera_frame


class BagFile(Camera):
    """
    Creates a bag file reader object

    Parameters
    ----------
    screen_width: number
        Resolution width of the pre-recorded .bag file
    screen_height: number
        Resolution height of the pre-recorded .bag file
    frame_rate: number
        Framerate of the pre-recorded .bag file
    filename: str
        Name of .bag file to read.
        Driver should find this by parsing arguments
    repeat: bool
        Whether to repeatedly loop through the bag file.
    """

    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        frame_rate: int,
        filename: str,
        repeat: bool = True,
        **kwargs
    ):
        super().__init__(screen_width, screen_height, frame_rate)

        self.filename = filename

        self.pipeline = rs.pipeline()

        # Create a config object
        self.config = rs.config()
        # Tell config that we will use a recorded device from file
        # to be used by the pipeline through playback.
        rs.config.enable_device_from_file(self.config, self.filename, repeat)

    def __iter__(self):
        """
        Iterate through each frame in the bag file.
        NOTE: This loops through the video continuously when repeat is True.

        Yields
        ------
        depth image[1 channel]: numpy array
        color image[3 channel]: numpy array
            in RGB format
        """
        # Start streaming from file
        self.pipeline.start(self.config)

        align_to = rs.stream.color
        align = rs.align(align_to)

        more_frames = True

        while more_frames:
            try:
                # returns the next color/depth frame
                frames = self.pipeline.wait_for_frames()
            except:  # next frame not received within 5 seconds, assume end of file
                # will only happen if repeat is False
                more_frames = False
                break

            # Align the depth frame to color frame
            aligned_frames = align.process(frames)

            # Get aligned frames
            # aligned_depth_frame is a 640x480 depth image
            aligned_depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()

            depth_image = np.asanyarray(aligned_depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())
            color_image = color_image[:, :, ::-1]  # shifts colors back to normal

            yield depth_image, color_image

    def display_in_window(self, clipping: bool = False) -> None:
        """
        Displays the depth/color image streams, separately, in one window. Will repeat if repeat is True.

        Parameters
        ----------
        clipping: bool
            defaults to false, can be set true to remove data from the images
            beyond a given distance from the camera

        Returns
        -------
        None
        """
        for depth_image, color_image in self:
            # Remove background - Set pixels further than clipping_distance to grey
            grey_color = 153
            depth_image_3d = np.dstack((depth_image, depth_image, depth_image))

            # render depth/color images
            depth_colormap = cv2.applyColorMap(
                cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET
            )

            if clipping:
                bg_removed = np.where((depth_image_3d <= 0), grey_color, color_image)
                images = np.hstack((bg_removed, depth_colormap))
            else:
                images = np.hstack((color_image, depth_colormap))

            cv2.namedWindow("Depth/Color Stream", cv2.WINDOW_NORMAL)
            cv2.resizeWindow("Depth/Color Stream", self.width, int(self.height / 2))
            cv2.imshow("Depth/Color Stream", images)

            key = cv2.waitKey(1)

            if key == ord("c"):
                save_camera_frame(depth_image, color_image)

            # if pressed 'q' or escape (27) exit program
            if (
                key == ord("q")
                or key == 27
                or cv2.getWindowProperty("Depth/Color Stream", 0) == -1
            ):
                cv2.destroyAllWindows()
                break

    def save_as_img(self, folder_name: str = "new_set") -> None:
        """
        Iterates through the .bag file and saves color and depth frames as .jpg and .npy files respectively.
        NOTE: Due to how .bag file is read, the number of frames saved may vary. Not every frame of the file is saved.
        NOTE: Requires repeat to be false, or .bag file will be iterated over multiple times,
              potentially resulting in repeat images.

        Paramters
        ---------
        folder_name: str
            The name of the folder to save the frames to.

        Returns
        -------
        None.
        """
        DIRECTORY = folder_name
        if not os.path.isdir(DIRECTORY):
            os.mkdir(DIRECTORY)

        for depth_image, color_image in self:
            save_camera_frame(depth_image, color_image, DIRECTORY)

        return


if __name__ == "__main__":
    """
    Tool for viewing bag files or saving bag files as a dataset of images.

    Command Line Arguments
    -f, --file_location {location}
        Required. Bag file to use.
    -n, --no_repeat
        Don't repeat iteration through file.

    """
    import argparse

    parser = argparse.ArgumentParser(description="Must specify file location.")

    parser.add_argument(
        "-f",
        "--file_location",
        type=str,
        help="Location of the .bag file to run. Required Argument.",
    )
    parser.add_argument(
        "-n",
        "--no_repeat",
        action="store_true",
        help="Don't repeat iteration through file.",
    )
    parser.add_argument(
        "-s",
        "--save_set",
        action="store_true",
        help="Save as dataset instead of viewing in window",
    )

    args = parser.parse_args()

    # no file location specified, cannot continue
    if not args.file_location:
        raise RuntimeError("No file location specified.")

    repeat = not args.no_repeat
    if args.save_set:
        repeat = False

    if not args.save_set:
        BagFile(
            screen_width=720,
            screen_height=1080,
            frame_rate=0,
            filename=args.file_location,
            repeat=repeat,
        ).display_in_window()
    else:
        BagFile(
            screen_width=720,
            screen_height=1080,
            frame_rate=0,
            filename=args.file_location,
            repeat=repeat,
        ).save_as_img()
