"""
Bounding boxes to convey information to flight code.
"""

from enum import Enum


class ObjectType(Enum):
    """
    All possible object types.
    """

    AVOID = "avoid"
    PYLON = "pylon"
    MODULE = "module"
    BOAT = "boat"
    UNKNOWN = "unknown"
    TEXT = "text"


class BoundingBox:
    """
    The bounding box around an object, a method of conveying information
    to flight code.

    Parameters
    ----------
    verticies: list[tuple[int]]
        Four verticies as corners of box.
    object_type: ObjectType
        Type of object.
    """

    def __init__(self, vertices: list, object_type: ObjectType):
        self.vertices: list = vertices
        self.object_type: ObjectType = object_type

    def __repr__(self) -> str:
        return f"BoundingBox[{id(self)}, {self.object_type}]: {str(self.vertices)}"


if __name__ == "__main__":
    verts = [(1, 3), (2, 4)]

    bb = BoundingBox(verts, ObjectType.PYLON)

    print(bb)
