"""
Vision camera related tests.
"""
import sys, os
parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import unittest
from unittest.mock import patch

import numpy as np
import airsim

from vision.camera import bag_file
from vision.camera import realsense
from vision.camera import sim_camera


COLOR_IMAGE = np.arange(0, 10).reshape(-1, 1, 1) + np.arange(0, 10).reshape(1, -1, 1) + np.arange(0, 3).reshape(1, 1, -1)
DEPTH_IMAGE = np.arange(0, 20).reshape(-1, 1) + np.arange(0, 20).reshape(1, -1)


## bag_file, realsense
class FakeRSFrame:
    def __init__(self, data):
        self.data = data

    def get_data(self):
        return self.data


class FakeRSFrameContainer:
    def get_color_frame(self, *args, **kwargs):
        return FakeRSFrame(np.copy(COLOR_IMAGE))

    def get_depth_frame(self, *args, **kwargs):
        return FakeRSFrame(np.copy(DEPTH_IMAGE))


class FakeRSAlign:
    """
    Mocking pyrealsense2 align.
    """
    def process(self, frame):
        return frame


class FakeRSPipeline:
    """
    Mocking pyrealsense2 pipeline.
    """
    def start(self, *args, **kwargs):
        pass

    def wait_for_frames(self, *args, **kwargs):
        return FakeRSFrameContainer()


## sim_camera
class FakeAirsimResponse:
    def __init__(self, data):
        self.data = data

    @property
    def height(self):
        return self.data.shape[0]

    @property
    def width(self):
        return self.data.shape[1]

    @property
    def depth(self):
        return 1 if len(self.data.shape) == 2 else self.data.shape[2]

    @property
    def image_data_uint8(self):
        if self.depth == 1:
            return np.array(np.dstack([self.data] * 3), dtype='uint8')

        return np.array(self.data, dtype='uint8')


class FakeAirsimClient:
    def simGetImages(self, info):
        target = info[0].image_type

        if target is airsim.ImageType.Scene:
            return [FakeAirsimResponse(np.copy(COLOR_IMAGE))]
        elif target is airsim.ImageType.DepthVis:
            return [FakeAirsimResponse(np.copy(DEPTH_IMAGE))]
        else:
            raise ValueError(f"Unrecognized airsim type '{target}'")


## testcase
class TestCamera(unittest.TestCase):
    """
    Testing the camera class.
    """
    def patch_camera(func):
        """
        Patch all necessary camera core components.
        """
        @patch.object(bag_file.rs.pipeline, '__new__', return_value=FakeRSPipeline())
        @patch.object(bag_file.rs.align, '__new__', return_value=FakeRSAlign())
        @patch.object(sim_camera.airsim.MultirotorClient, '__new__', return_value=FakeAirsimClient())
        def patched_function(*args, **kwargs):
            return func(*args, **kwargs)

        return patched_function

    def run_all_types(func):
        """
        Wrapper creating subtest for every type of object.
        """
        def run_all(self, *mocks):
            for obj in [bag_file.BagFile, realsense.Realsense, sim_camera.SimCamera]:
                with self.subTest(i=obj.__name__):
                    self._get_camera = self._set_obj(obj)

                    func(self)

        return run_all

    def _set_obj(self, obj):
        """
        Create generator that will render only specific object.
        """
        def _get_camera(**kwargs):
            config = {
                'screen_width': 0,
                'screen_height': 0,
                'frame_rate': 0,
                'filename': '',
                }
            config.update(kwargs)

            camera = obj(**config)

            return camera

        return _get_camera

    @patch_camera
    @run_all_types
    def test_iter(self):
        """
        Testing Pipeline.run_algorithm.

        Settings
        --------
        vid_file: str
            Video filename to give to ReadBag.
        env: Environment
            Environment model to update.
        alg_time: int
            Max time to run pipeline, measured in video frames.

        Effects
        -------
        Iterates through ReadBag and passes images into ObstacleFinder.
        The bounding boxes generated given to env, and further plot obstacles.
        """
        ## Ensure runs without error & correct values passed around
        camera = self._get_camera()

        i = 0
        for depth, color in camera:
            i += 1
            try:
                np.testing.assert_array_equal(color, COLOR_IMAGE)
            except AssertionError:
                np.testing.assert_array_equal(color[:, :, ::-1], COLOR_IMAGE)

            try:
                np.testing.assert_array_equal(depth, np.dstack([DEPTH_IMAGE] * 3))            
            except AssertionError:
                np.testing.assert_array_equal(depth, DEPTH_IMAGE)

            if i > 3:
                break


if __name__ == '__main__':
    unittest.main()
