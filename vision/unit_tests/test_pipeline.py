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

from multiprocessing import Queue

from vision import pipeline as PIPELINE


class FakeObstacleFinder:
    def __init__(self, *args, **kwargs):
        self.keypoints = []

    def find(*args, **kwargs):
        return list(range(12))


class TestPipeline(unittest.TestCase):
    """
    Testing the pipeline class.
    """

    @staticmethod
    def _get_pipeline(**kwargs):  ## Patch ReadBag, ObstacleFinder, env, plot_obstacles
        env = Mock()
        env.update = Mock()

        config = {
            "env": env,
        }
        config.update(kwargs)

        pipeline = PIPELINE.Pipeline(Queue(), Queue(), config["camera"])

        # for key, value in config.items():
        #    setattr(pipeline, key, value)

        return pipeline

    def patch_pipeline(func):
        image_generator = (
            (np.ones((300, 300)), np.ones((300, 300))) for _ in range(1000)
        )

        @patch.object(
            PIPELINE.ObstacleFinder, "__new__", return_value=FakeObstacleFinder()
        )
        def patched_function(*args, **kwargs):
            return func(*args, **kwargs)

        return patched_function

    @patch_pipeline
    def test_run(self, Obstacle__init__):
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
        ## Ensure runs without error
        flight_communication = type(
            "FlightCommunication", (object,), {"get_state": lambda: "early_laps"}
        )

        camera = type(
            "Camera",
            (object,),
            {
                "__iter__": lambda: (
                    (np.ones((3, 3, 3), dtype="uint8"), np.ones((3, 3), dtype="uint8"))
                    for _ in range(100)
                )
            },
        )

        pipeline = self._get_pipeline(
            flight_communication=flight_communication, camera=camera
        )
        pipeline.run("start")


if __name__ == "__main__":
    unittest.main()
