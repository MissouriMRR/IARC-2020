from vision.blob.object_type import ObjectType

class Rectangle:
    """
    Constructs a 3D rectangular prism using 8 (x, y, z) coordinates

    Parameters
    ----------
    top_left_near: tuple[float]
        top (-y), left (-x), and near (-z) coordinate
    top_right_near: tuple[float]
        top (-y), right (+x), and near (-z) coordinate
    bottom_right_near: tuple[float]
        bottom (+y), right (+x), and near (-z) coordinate
    bottom_left_near: tuple[float]
        bottom (+y), left (-x), and near (-z) coordinate
    top_left_far: tuple[float]
        top (-y), left (-x), and far (+z) coordinate
    top_right_far: tuple[float]
        top (-y), right (+x), and far (+z) coordinate
    bottom_right_far: tuple[float]
        bottom (+y), right (+x), and far (+z) coordinate
    bottom_left_far: tuple[float]
        bottom (+y), left (-x), and far (+z) coordinate
    """
    def __init__(self, top_left_near, top_right_near, bottom_right_near, bottom_left_near, top_left_far, top_right_far, bottom_right_far, bottom_left_far):
        self.top_left_near = top_left_near
        self.top_right_near = top_right_near
        self.bottom_right_near = bottom_right_near
        self.bottom_left_near = bottom_left_near
        self.top_left_far = top_left_far
        self.top_right_far = top_right_far
        self.bottom_right_far = bottom_right_far
        self.bottom_left_far = bottom_left_far

class Blob:
    """
    Constructs a Rectangle associated with an object type/label

    Parameters
    ----------
    bounding_box: Rectangle
        defines the 3D space taken up by the blob
    object_type: ObjectType
        enum that describes/labels the blob
    """
    def __init__(self, bounding_box, object_type):
        if not isinstance(bounding_box, Rectangle):
            print('bounding_box should be a Rectangle, got', bounding_box)
        if not isinstance(object_type, ObjectType):
            print('object_type should be an ObjectType, got', object_type)
        self.bounding_box = bounding_box
        self.object_type = object_type