class BoundingBox:
    def __init__(self, vertices, object_type):
        self.vertices = str(vertices)
        self.object_type = object_type

    def __repr__(self):
        return self.vertices
