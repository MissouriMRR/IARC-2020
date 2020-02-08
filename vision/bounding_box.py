"""
Bounding boxes to convey information to flight code.
"""


class BoundingBox:
    """
    The bounding box of an object.

    Parameters
    ----------
    verticies: list[tuple[int]]
        Four verticies as corners of box.
    object_type: Enum
        Type of object.
    """
    def __init__(self, vertices, object_type):
        self.vertices = vertices
        self.object_type = object_type

    def __repr__(self):
        return self.vertices
