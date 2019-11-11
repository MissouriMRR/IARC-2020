import cv2
import numpy as np
from colors import Colors
from Shape import Shape, ShapeFill


class Circle(Shape):
    """A class which represents a circle"""
    DEFAULT_RADIUS = 5

    def __init__(self, x, y, radius=DEFAULT_RADIUS):
        super().__init__()
        self.x = x
        self.y = y
        self.radius = radius

    @property
    def diameter(self):
        return self.radius * 2

    def is_inside(self, x, y):
        return (self.x-x)**2+(self.y-y)**2<=self.radius**2
   
    def get_bounds(self):
        from Rectangle import Rectangle
        return Rectangle(self.x-self.radius, self.y-self.radius, self.diameter, self.diameter)

    def _draw(self, img, color, thickness):
        cv2.circle(img, (self.x, self.y), self.radius, color, thickness)


if __name__ == '__main__':
    # create a white canvas
    w, h = (512, 512)
    canvas = np.ones((w, h, 3), dtype=np.uint8)*255
    # draw a circle in the top left corner with default settings
    circle = Circle(0, 0, 50)
    circle.draw(canvas)

    def display():
        cv2.imshow('test', canvas)
        cv2.waitKey(0)

    try:
        # display the current image and wait for a key to be pressed before continuing
        display()
        # test transparent outlines and try another color
        circle = Circle(w, 0, 50)
        circle.draw(canvas, color=Colors.RED, alpha=.5)
        display()
        # test out transparent filled shapes with debug text
        circle = Circle(int(w//2), int(h//2), 50)
        circle.debug_string = 'test'
        circle.draw(canvas, color=Colors.BLUE, alpha=.1, fill=ShapeFill.FILLED)
        display()
        # test out filled shape without transparency and html colors
        circle = Circle(0, h, 50)
        circle.draw(canvas, color=Color.from_hex('#ff7b25'), fill=ShapeFill.FILLED)
        display()

        # display a darker shade of the color from before
        circle = Circle(w, h, 50)
        circle.draw(canvas, color=Color.from_hex('#ff7b25').lerp(Colors.BLACK, .2), fill=ShapeFill.FILLED)
        display()
    finally:
        cv2.destroyAllWindows()
