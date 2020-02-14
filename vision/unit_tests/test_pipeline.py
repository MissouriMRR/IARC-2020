"""
Vision pipeline related tests.
"""
import sys, os
parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import unittest
from unittest.mock import patch, Mock
import numpy as np

# from vision.pipeline import Pipeline
from vision.pipeline import Pipeline

from camera import bag_file

class TestPipeline(unittest.TestCase):
    """
    Testing the pipeline class.
    """
    def _get_pipeline(self, **kwargs):  ## Patch ReadBag, ObstacleFinder, env, plot_obstacles
        env = Mock()
        env.update = Mock()

        config = {
            "env": env,
            "vid_file": "",
            "alg_time": 1,
        }
        config.update(kwargs)

        pipeline = Pipeline(None, None, None)

        for key, value in config.items():
            setattr(pipeline, key, value)

        return pipeline, env

    def patch_pipeline(func):
        image_generator = ((np.ones((300, 300)), np.ones((300, 300))) for _ in range(1000))

        @patch('pipeline.BagFile.__init__', autospec=True, return_value=None)
        @patch('pipeline.BagFile.__iter__', autospec=True, return_value=image_generator)
        @patch('pipeline.import_params.import_params')
        @patch('pipeline.ObstacleFinder.__init__', return_value=None)
        @patch('pipeline.ObstacleFinder.find', return_value=list(range(12)))
        def patched_function(*args, **kwargs):
            return func(*args, **kwargs)

        return patched_function

    @patch_pipeline
    def test_run(self, Obstacle__find__, Obstacle__init__, import_params, Bag__iter__, Bag__init__):
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
        VID_FILE = "testttttttt"

        pipeline, env = self._get_pipeline(vid_file=VID_FILE)
        pipeline.run_algorithm()

        # obstacle(0, 0, 0, filename)
        self.assertEqual(Bag__init__.call_args_list[0][0][-1], VID_FILE)

        # obstacle.find(image) -> [bounding_box]
        self.assertIsInstance(Obstacle__find__.call_args_list[0][0][0], np.ndarray)

        # env.update <- [bounding_box]
        self.assertIsInstance(env.update.call_args_list[0][0][0], list)



if __name__ == '__main__':
    unittest.main()
