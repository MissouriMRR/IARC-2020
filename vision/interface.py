"""
A model of the environment around the drone.
"""

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)

from vision.bounding_box import BoundingBox


class Environment:
    """
    The percieved environment.
    """

    def __init__(self):
        self.bounding_boxes = []

    def __iter__(self) -> BoundingBox:
        """
        Iterate over all bounding boxes.

        Yields
        ------
        BoundingBox - The next bounding box.
        """
        i = 0
        while True:
            try:
                i %= len(self.bounding_boxes)
                yield self.bounding_boxes[i]
                i += 1
            except ZeroDivisionError:
                yield None

    def update(self, bounding_boxes: BoundingBox) -> None:
        """
        Update environment.

        Parameters
        ----------
        bounding_boxes: list[BoundingBox]
            New environment data.
        """
        self.bounding_boxes = bounding_boxes
