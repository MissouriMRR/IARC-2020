from vision.blob.constants import ObjectType

class Rectangle:
    def __init__(self, top_left_coord, top_right_coord, bottom_right_coord, bottom_left_coord):
        self.top_left_coord = top_left_coord
        self.top_right_coord = top_right_coord
        self.bottom_right_coord = bottom_right_coord
        self.bottom_left_coord = bottom_left_coord

class Blob:
    def __init__(self, bounding_box, object_type):
        if not isinstance(bounding_box, Rectangle):
            print('bounding_box should be a Rectangle, got', bounding_box)
        if not isinstance(object_type, ObjectType):
            print('object_type should be an ObjectType, got', object_type)
        self.bounding_box = bounding_box
        self.object_type = object_type