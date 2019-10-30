#rectangle object
#environment object full of rectangle
#iter function as generator
#updater function
#unique identifier of rectangles


class Rectangle:
    def __init__(self, vertices, type):
        self.vertices = vertices
        self.type = type


if __name__ == '__main__':
    rects = []
    rect1 = Rectangle(4, ",")
    rect2 = Rectangle(8, ",")
    rect3 = Rectangle(2, ",")
    rect4 = Rectangle(6, ",")
    rect5 = Rectangle(7, ",")
    rects.append(rect1)
    rects.append(rect2)
    rects.append(rect3)
    rects.append(rect4)
    rects.append(rect5)

# information needs to be accessible/ function where generator gets called


class Environment:

    def __init__(self, rect):
        self.rect = rect