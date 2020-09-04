"""
A model of the environment around the drone.
"""


class Environment:
    """
    The percieved environment.
    """
    def __init__(self):
        self.bounding_boxes = []

    def __iter__(self):
        """
        Iterate over all bounding boxes.

        Yields
        ------
        BoundingBox
        """
        i = 0
        while True:
            try:
                i %= len(self.bounding_boxes)
                yield self.bounding_boxes[i]
                i += 1
            except ZeroDivisionError:
                yield None

    def update(self, bounding_boxes):
        """
        Update environment.

        Parameters
        ----------
        bounding_boxes: list[BoundingBox]
            New environment data.
        """
        self.bounding_boxes = bounding_boxes
