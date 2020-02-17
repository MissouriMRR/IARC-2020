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

from vision.camera import *


class TestPipeline(unittest.TestCase):
    """
    Testing the pipeline class.
    """
    def patch_camera(func):
        #@patch('pipeline.BagFile.__init__', autospec=True, return_value=None)
        def patched_function(*args, **kwargs):
            return func(*args, **kwargs)

        return patched_function

    def run_all_types(func):
        """
        Wrapper creating subtest for every type of object.
        """
        def run_all(self):
            for obj in []:  # BagFile, Realsense, SimCamera]:
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

    @run_all_types
    @patch_camera
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
        for color, depth in camera:
            i += 1
            # assert correct color and depth given(that I patched)

            if i > 3:
                break


if __name__ == '__main__':
    unittest.main()
