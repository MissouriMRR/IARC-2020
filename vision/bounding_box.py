"""
Bounding boxes to convey information to flight code.
"""
from enum import Enum


class ObjectType(Enum):
    """
    All possible object types.
    """
    AVOID = 'avoid'
    PYLON = 'pylon'
    MODULE = 'module'
    BOAT = 'boat'
    UNKNOWN = 'unknown'


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
        return f"BoundingBox[{id(self)}, {self.object_type}]: {str(self.vertices)}"


if __name__ == '__main__':
    verts = [(1, 3), (2, 4)]

    bb = BoundingBox(verts, ObjectType.PYLON)

    print(bb)
