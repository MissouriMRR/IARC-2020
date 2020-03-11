"""
SimCamera is a child class of camera, designed to be used for simulator depth/color streams
"""
import os
import sys

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import cv2
import numpy as np
import airsim
try:
    from vision.camera.template import Camera
except ImportError:
    from template import Camera


class SimCamera(Camera):
    """
    Creates an airsim camera object
    """
    def __init__(self, **kwargs):
        super().__init__(-1, -1, -1)  # for screen_width, screen_height, and framerate, unnecessary
        self.client = airsim.MultirotorClient()

    def __iter__(self):
        """
        Iterate through each frame in the airsim cameras
        NOTE: The airsim must be running currently for __iter__ to work

        Returns
        -------
        depth image[1 channel]: numpy array
        color image[3 channel]: numpy array
            in RGB format
        """
        while True:
            depth_responses = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.DepthVis, False, False)])
            depth_response = depth_responses[0]

            scene_responses = self.client.simGetImages([airsim.ImageRequest("0", airsim.ImageType.Scene, False, False)])
            scene_response = scene_responses[0]

            depth_np_1d = np.frombuffer(depth_response.image_data_uint8, dtype=np.uint8)
            color_np_1d = np.frombuffer(scene_response.image_data_uint8, dtype=np.uint8)

            depth_np = depth_np_1d.reshape(depth_response.height, depth_response.width, 3)
            color_np = color_np_1d.reshape(scene_response.height, scene_response.width, 3)

            yield depth_np, color_np

    def display_in_window(self):
        """
        Displays the depth/color image streams, separately, in one window
        """
        for depth_image, color_image in self:
            # Render images
            depth_colormap = cv2.applyColorMap(
                cv2.convertScaleAbs(depth_image, alpha=0.03),
                cv2.COLORMAP_JET)

            images = np.hstack((color_image, depth_colormap))

            cv2.namedWindow('Depth/Color Stream', cv2.WINDOW_AUTOSIZE)
            cv2.imshow('Depth/Color Stream', images)

            key = cv2.waitKey(0)

            # Press esc or 'q' to close the image window
            if key == ord('q') or key == 27 or cv2.getWindowProperty('Depth/Color Stream', 0) == -1:
                cv2.destroyAllWindows()
                break


if __name__ == '__main__':
    ## Display algorithm output on simulator
    import json
    from vision.obstacle.obstacle_finder import ObstacleFinder
    from vision.common.import_params import import_params

    camera = SimCamera()

    prefix = 'vision' if os.path.isdir("vision") else ''
    config_filename = os.path.join(prefix, 'obstacle', 'config.json')

    with open(config_filename, 'r') as config_file:
        config = json.load(config_file)

    obstacle_finder = ObstacleFinder(params=import_params(config))

    for depth_image, color_image in camera:
        bboxes = []

        bboxes = obstacle_finder.find(color_image, depth_image)

        from vision.common.blob_plotter import plot_blobs
        plot_blobs(obstacle_finder.keypoints, color_image)
