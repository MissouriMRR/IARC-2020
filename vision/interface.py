#rectangle object
#environment object full of rectangle
#iter function as generator
#updater function
#unique identifier of rectangles
#submit pull reques when completing single thread

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

    def __init__(self):
        self.rects = []

    def __iter__(self):
        self.length = len(self.rects)
        i = 0
        while True:
            try:
                i %= len(self.rects)
                yield self.rects[i]
                i += 1
            except ZeroDivisionError:
                yield None

    def update(self, rects):
        self.rects = rects

env = Environment()
for i in env:
    print(i)