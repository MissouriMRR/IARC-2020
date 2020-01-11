"""
Geometry to use w/ UI
"""
from enum import Enum

import cv2
import numpy as np

from colors import Colors


class ShapeFill(Enum):
    """Defines how a shape may be drawn"""
    FILLED = -1
    OUTLINE = 0


class Shape(object):
    """Generic shape base class"""
    DEFAULT_THICKNESS = 2
    DEFAULT_COLOR = Colors.GREEN

    def _draw(self, img, color, thickness):
        raise NotImplementedError(f"_draw not implemented for {type(self)}!")

    def draw(self, img, color=DEFAULT_COLOR, thickness=DEFAULT_THICKNESS, alpha=1., fill=ShapeFill.OUTLINE):
        color = color.value if hasattr(color, 'value') else color

        if fill == ShapeFill.FILLED:
            thickness = ShapeFill.FILLED.value

        if alpha < 1:
            overlay = img.copy()
            self._draw(overlay, color, thickness)

            cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
        else:
            self._draw(img, color, thickness)


class Rectangle(Shape):
    """A class which represents a rectangle"""

    def __init__(self, x, y, w, h):
        super().__init__()

        self.x, self.y = int(x), int(y)
        self.w, self.h = int(w), int(h)

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
        return Rectangle(self.x-self.radius, self.y-self.radius, self.diameter, self.diameter)

    def _draw(self, img, color, thickness):
        cv2.circle(img, (self.x, self.y), self.radius, color, thickness)


class ResizableBox(object):
    """A resizable bounding box useful for making annotations or selecting ROIs."""
    HANDLE_RADIUS = 5
    OPACITY = .2
    HANDLE_OPACITY = .8
    DARKEN_HANDLE_BY = .5

    def __init__(self, x, y, w, h):
        self._box = Rectangle(x, y, w, h)
        self._circles = []
        self._corners = [(x, y), (x+w, y), (x+w, y+h), (x, y+h)]
        self._is_moving_box = False
        self._where_was_lbutton_pressed = None
        self._is_resizing_box = False
        self._selected_handle = None
        self._invert_resize_y_axis = False
        self._invert_resize_x_axis = False
        self.changed = False

        for corner in self._corners:
            self._circles.append(Circle(*corner, radius=self.HANDLE_RADIUS))

        self._handle_color = Colors.GRAY
        self._darker_handle_color = Colors.BLACK
        self._handle_colors = {circle: Colors.GRAY for circle in self._circles}
        self._righthand_circles = self._circles[1:3]
        self._lefthand_circles = self._circles[0:len(self._circles):len(self._circles)-1]
        self._bottom_circles = self._circles[2:len(self._circles)]

    def draw(self, img, color=Shape.DEFAULT_COLOR):
        self._box.draw(img, color, alpha=ResizableBox.OPACITY, fill=ShapeFill.FILLED)
        self._box.draw(img, color, fill=ShapeFill.OUTLINE)

        for circle in self._circles:
            circle.draw(img, self._handle_colors[circle], fill=ShapeFill.FILLED)
            circle.draw(img, Colors.BLACK, fill=ShapeFill.OUTLINE)

    @property
    def x(self):
        return self._box.x

    @x.setter
    def x(self, value):
        delta_x = value - self._box.x
        self._box.x = value

        for circle in self._circles:
            circle.x += delta_x

    @property
    def y(self):
        return self._box.y

    @y.setter
    def y(self, value):
        delta_y = value - self._box.y
        self._box.y = value

        for circle in self._circles:
            circle.y += delta_y

    @property
    def w(self):
        return self._box.w

    @w.setter
    def w(self, value):
        if self._invert_resize_x_axis:
            self.x += self._box.w - value

        self._box.w = value

        for circle in self._righthand_circles:
            circle.x = self._box.x1

    @property
    def h(self):
        return self._box.h

    @h.setter
    def h(self, value):
        if self._invert_resize_y_axis:
            self.y += self._box.h - value

        self._box.h = value

        for circle in self._bottom_circles:
            circle.y = self._box.y1

    @property
    def x1(self):
        return self._box.x1

    @property
    def y1(self):
        return self._box.y1

    def get_bounds(self):
        return self._box.get_bounds()

    def scale_by(self, scale):
        return self._box.scale_by(scale)

    def on_mouse_event(self, event, x, y, flags, params):
        if event == cv2.EVENT_MOUSEMOVE:
            if self._is_moving_box:
                delta_x, delta_y = self._where_was_lbutton_pressed
                self.x = x + delta_x
                self.y = y + delta_y

            elif self._is_resizing_box:
                if not self._invert_resize_x_axis:
                    self.w = x - self.x
                else:
                    self.w = self.x1 - x

                if not self._invert_resize_y_axis:
                    self.h = y - self.y
                else:
                    self.h = self.y1 - y

            elif (self._selected_handle is not None and not self._selected_handle.is_inside(x, y)) or self._selected_handle is None:
                if self._selected_handle is not None:
                    self._handle_colors[self._selected_handle] = self._handle_color
                    self._selected_handle = None

                for circle in self._circles:
                    if circle.is_inside(x, y):
                        self._selected_handle = circle
                        self._handle_colors[circle] = self._darker_handle_color

                        if self._selected_handle.x < self.x1:
                            self._invert_resize_x_axis = True
                        else:
                            self._invert_resize_x_axis = False

                        if self._selected_handle.y < self.y1:
                            self._invert_resize_y_axis = True
                        else:
                                self._invert_resize_y_axis = False

        elif event == cv2.EVENT_LBUTTONDOWN:
            if self._selected_handle is not None:
                self._is_resizing_box = True
                self._where_was_lbutton_pressed = (self._selected_handle.x, self._selected_handle.y)
            if self._box.is_inside(x, y) and not self._is_resizing_box:
                self._where_was_lbutton_pressed = (self.x - x, self.y - y)
                self._is_moving_box = True

        elif event == cv2.EVENT_LBUTTONUP:
            self._is_moving_box = False
            self._is_resizing_box = False
            self._where_was_lbutton_pressed = None

        self.changed = self._is_moving_box or self._is_resizing_box


if __name__ == '__main__':
    from window import Window

    # create a white canvas
    w, h = (512, 512)
    canvas = np.ones((w, h, 3), dtype=np.uint8)*255

    # create a resizable box
    box = ResizableBox(int(w/2)-25, int(h/2)-25, 50, 50)

    with Window('test') as window:
        window.set_mouse_callback(box.on_mouse_event)

        while not window.should_quit:
            frame = canvas.copy()
            box.draw(frame)
            window.draw(frame)
