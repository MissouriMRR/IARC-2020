"""
Detects obstacles in videos using ObstacleFinder
"""

import os
import json
from vision.blob.blobfind import BlobFinder
from vision.util.import_params import import_params

class ObstacleVideo:

    def __init__(self, blob_finder):
        self.blob_finder = blob_finder

    @property
    def blob_finder(self):
        """
        This function is called every time self.blob_finder is run
        """
        return self._blob_finder

    @blob_finder.setter
    def blob_finder(self, value):
        """
        Defines behavior of self.blob_finder = value
        """
        if not isinstance(value, BlobFinder):
            raise ValueError(f"Requires instance of BlobFinder, got {type(value)}")
        self._blob_finder = value

    def find_obstacles(self, video):
        for frame in video:
            self.blob_finder.find(frame)

if __name__ == '__main__':
    prefix = 'vision' if os.path.isdir("vision") else ''
    vid_folder = os.path.join(prefix, 'vision_videos', 'obstacle')
    config_filename = os.path.join(prefix, 'blob', 'config.json')

    with open(config_filename, 'r') as config_file:
        config = json.load(config_file)

    blob_finder = BlobFinder(params=import_params(config))
    video = ObstacleVideo(blob_finder)

    for vid_file in os.listdir(vid_folder):
        video.find_obstacles(vid_file)
