import cv2
import numpy as np
from colors import Colors
from Shape import Shape, ShapeFill


class Rectangle(Shape):
    """A class which represents a rectangle"""

    def __init__(self, x, y, w, h):
        super().__init__()
        self.x = int(x)
        self.y = int(y)
        self.w = int(w)
        self.h = int(h)

    def is_inside(self, x, y):
        return self.x <= x <= self.x1 and self.y <= y <= self.y1

    @property
    def area(self):
        return self.w * self.h

    @property 
    def x1(self):
        return self.x + self.w

    @property
    def y1(self):
        return self.y + self.h

    @property
    def midpoint(self):
        return (int((self.x+self.x1)//2), int((self.y + self.y1)//2))

    def get_bounds(self):
        return self

    def scale_by(self, scale):
        return Rectangle(self.x//scale, self.y//scale, self.w//scale, self.h//scale)

    def get_roi(self, img):
        return img[self.y:self.y1, self.x:self.x1]

    def _draw(self, img, color, thickness):
        cv2.rectangle(img, (self.x, self.y), (self.x1, self.y1), color, thickness)

if __name__ == '__main__':
    # create a white canvas
    w, h = (512, 512)
    canvas = np.ones((w, h, 3), dtype=np.uint8)*255
    # draw a rectangle in the top left corner with default settings
    rectangle = Rectangle(0, 0, 50, 50)
    rectangle.draw(canvas)

    def display():
        cv2.imshow('test', canvas)
        cv2.waitKey(0)

    try:
        # display the current image and wait for a key to be pressed before continuing
        display()
        # test transparent outlines and try another color
        rectangle = Rectangle(w-50, 0, 50, 50)
        rectangle.draw(canvas, color=Colors.RED, alpha=.5)
        display()
        # test out transparent filled shapes with debug text
        rectangle = Rectangle(int(w//2)-25, int(h//2)-25, 50, 50)
        rectangle.debug_string = 'test'
        rectangle.draw(canvas, color=Colors.BLUE, alpha=.1, fill=ShapeFill.FILLED)
        display()
        # test out filled shape without transparency and html colors
        rectangle = Rectangle(0, h-50, 50, 50)
        rectangle.draw(canvas, color=Color.from_hex('#ff7b25'), fill=ShapeFill.FILLED)
        display()

        # display a darker shade of the color from before
        rectangle = Rectangle(w-50, h-50, 50, 50)
        rectangle.draw(canvas, color=Color.from_hex('#ff7b25').lerp(Colors.BLACK, .2), fill=ShapeFill.FILLED)
        display()
    finally:
        cv2.destroyAllWindows()
