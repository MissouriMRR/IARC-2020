"""
Detects obstacles in videos using ObstacleFinder
"""

from vision.blob.blobfind import BlobFinder

class ObstacleVideo:

    def __init__(self, blob_finder=None):
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