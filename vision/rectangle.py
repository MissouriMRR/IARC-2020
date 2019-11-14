class Rectangle:
    def __init__(self, vertices, type):
        self.vertices = str(vertices)
        self.type = type

    def __repr__(self):
        return self.vertices