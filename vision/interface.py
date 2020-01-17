
"""The Environment class will manage the other objects in the environment"""


class Environment:

    # list of rectangles in environment
    def __init__(self):
        self.bounding_boxes = []

    # iterator of the bounding boxes list
    def __iter__(self):
        i = 0
        while True:
            try:
                i %= len(self.bounding_boxes)
                yield self.bounding_boxes[i]
                i += 1
            except ZeroDivisionError:
                yield None

    # updates bounding boxes list
    def update(self, bounding_boxes):
        self.bounding_boxes = bounding_boxes
