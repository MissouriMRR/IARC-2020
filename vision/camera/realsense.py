"""
The Realsense class is a child class of the camera, designed to be used for realsense depth cameras
"""
import sys, os

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


class Realsense(Camera):
    """
    Creates a realsense camera object

    Parameters
    ----------
    screen_width: number
        Resolution width of the pre-recorded .bag file
    screen_height: number
        Resolution height of the pre-recorded .bag file
    frame_rate: number
        Framerate of the pre-recorded .bag file
    serial_no: str
        Serial number of the realsense camera to stream from
        Defaults to empty, which reads if only one realsense is plugged in
    """

    def __init__(self, screen_width, screen_height, frame_rate, serial_no="", **kwargs):
        super().__init__(screen_width, screen_height, frame_rate)

        self.serialNumber = serial_no

        self.pipeline = rs.pipeline()

        # Create a config object
        self.config = rs.config()

        # a unique serial number for a camera, enables config to get data from a specific camera
        if self.serialNumber:
            self.config.enable_device(self.serialNumber)

        self.config.enable_stream(
            rs.stream.depth, self.width, self.height, rs.format.z16, self.framerate
        )
        self.config.enable_stream(
            rs.stream.color, self.width, self.height, rs.format.bgr8, self.framerate
        )

    def __iter__(self):
        """
        Iterates through each depth/color frame in the object

        Returns
        -----------
        depth image: np array, 1 channel
        color image: np array, 3 channels (in RGB format)
        """
        # Start streaming from file
        profile = self.pipeline.start(self.config)

        # Getting the depth sensor's depth scale (see rs-align example for explanation)
        # depth_sensor = profile.get_device().first_depth_sensor()
        # depth_scale = depth_sensor.get_depth_scale()

        align_to = rs.stream.color
        align = rs.align(align_to)

        while True:
            # returns the next color/depth frame
            frames = self.pipeline.wait_for_frames()

            # Align the depth frame to color frame
            aligned_frames = align.process(frames)

            # Get aligned frames
            # aligned_depth_frame is a 640x480 depth image
            aligned_depth_frame = aligned_frames.get_depth_frame()
            color_frame = aligned_frames.get_color_frame()

            depth_image = np.asanyarray(aligned_depth_frame.get_data())
            color_image = np.asanyarray(color_frame.get_data())

            yield depth_image, color_image

    def display_in_window(self, clipping=False):
        """
        Displays the depth/color image streams on repeat, separately, in one window

        Parameters
        -------
        clipping: boolean
            defaults to false, can be set true to remove data from the images
            beyond a given distance from the camera
        """
        for depth_image, color_image in self:
            grey_color = 153
            depth_image_3d = np.dstack((depth_image, depth_image, depth_image))

            # Render images
            depth_colormap = cv2.applyColorMap(
                cv2.convertScaleAbs(depth_image, alpha=0.03), cv2.COLORMAP_JET
            )

            if clipping:
                bg_removed = np.where((depth_image_3d <= 0), grey_color, color_image)
                images = np.hstack((bg_removed, depth_colormap))
            else:
                images = np.hstack((color_image, depth_colormap))

            cv2.namedWindow("Depth/Color Stream", cv2.WINDOW_AUTOSIZE)
            cv2.imshow("Depth/Color Stream", images)

            key = cv2.waitKey(1)

            if key == ord("c"):
                save_camera_frame(depth_image, color_image)

            # Press esc or 'q' to close the image window
            if (
                key == ord("q")
                or key == 27
                or cv2.getWindowProperty("Depth/Color Stream", 0) == -1
            ):
                cv2.destroyAllWindows()
                break

        self.pipeline.stop()


if __name__ == "__main__":
    Realsense(0, 0, 0).display_in_window()
