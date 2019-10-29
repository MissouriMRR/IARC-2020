
class Rectangle:
    def __init__(self, vertices, type):
        self.vertices = str(vertices)
        self.type = type

    def __repr__(self):
        return self.vertices


if __name__ == '__main__':
    rects = [
        Rectangle(4, ","),
        Rectangle(8, ","),
        Rectangle(2, ","),
        Rectangle(6, ","),
        Rectangle(7, ",")
    ]


"""This class will manage the other objects in the environment"""
class Environment:

    #list of rectangles in environment
    def __init__(self):
        self.rects = []

    #iterator of the rects list
    def __iter__(self):
        self.length = len(self.rects)
        i = 0
        while True:
            try:
                i %= self.length
                yield self.rects[i]
                i += 1
            except ZeroDivisionError:
                yield None

    #updates rects list
    def update(self, rects):
        self.rects = rects

    #calls update function and iterates
    def test(self, rects):
        self.update(rects)


if __name__ == "__main__":
    env = Environment()
    env.test(rects)
    for i in range(0, len(env.rects)):
        print(env.rects[i])
