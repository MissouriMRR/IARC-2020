"""
Keeps track of detected obstacles between frames
"""

import cv2
import numpy as np
from vision.bounding_box import BoundingBox


class Obstacle:
    """
    Properties of an obstacle in the frame.

    Parameters
    ----------
    bbox: BoundingBox
        bounding box of obstacle 
    """
    def __init__(self, bbox: BoundingBox):
        self.bounding_box = bbox
        self.center = np.mean(bbox)
        self.frames_persisted = 0


class ObstacleTracker:
    """
    Track obstacles between frames.
    """
    def __init__(self):
        self.MVMT_TOLERANCE = 0.10 # bounding box displacement tolerance per frame
        self.PERSISTENCE_THRESHOLD = 5 # number of frames for an obstacle to be considered consequential
        
        self.obstacles = np.array([]) # buffer that stores current Obstacles in view

    def _isSameObstacle(self, obj1: Obstacle, obj2: Obstacle) -> bool:
        """
        Returns True if the position of obj1 is within self.MVMT_TOLERANCE of obj2 

        Parameters
        ----------
        obj1: Obstacle
            The obstacle of reference
        obj2: Obstacle
            The obstacle in question
        """
        return obj1.center >= (1-self.MVMT_TOLERANCE)*obj2.center and obj1.center <= (1+self.MVMT_TOLERANCE)*obj2.center

    def update(self, new_obstacle_boxes: list) -> None:
        """
        Updates the stored obstacles buffer with new frame of bounding boxes

        Parameters
        ----------
        new_obstacle_boxes: list
            The new list of obstacles to update the buffer with
        
        Returns
        -------
        None
        """
        new_obstacles = np.array([])
        
        # transform the list of bounding boxes into an array of Obstacles
        for i in np.arange(new_obstacle_boxes.size()):
            new_obstacles[i] = Obstacle(new_obstacle_boxes[i])
        
        if(not self.obstacles):
            self.obstacles = new_obstacles
            return

        # create an array of obstacles that existed in the previous (buffer) frame and replace the buffer with it
        for i in np.arange(new_obstacles.size()):
            if(_isSameObstacle(new_obstacles[i], self.obstacles[i])):
                new_obstacles[i].frame_persisted = self.obstacles[i].frames_persisted + 1
        
        # update buffer
        self.obstacles = new_obstacles

    def getPersistentObstacles(self) -> list:
        """
        returns a list of bounding boxes that have been persistent for PERSISTENCE_THRESHOLD amount of frames

        Returns
        -------
        list[BoundingBox]
            a list of the persistent obstacle BoundingBoxes
        """
        persistent_obstacles = np.array([])

        # append only obstacles persistent for PERSISTENCE_THRESHOLD frames
        for i in np.arange(self.obstacles.size()):
            if(self.obstacles[i].frames_persisted == self.PERSISTENCE_THRESHOLD):
                persistent_obstacles.append(self.obstacles[i].bounding_box)
        
        return persistent_obstacles
