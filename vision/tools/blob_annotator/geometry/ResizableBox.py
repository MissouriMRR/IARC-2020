import cv2

from colors import Colors
from Shape import Shape, ShapeFill
from Rectangle import Rectangle
from Circle import Circle


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
            else:
                if self._is_resizing_box:
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
                        if circle.is_inside(x,y):
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
    from ui.Window import Window
    import numpy as np

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


