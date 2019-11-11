from enum import Enum
import cv2
from colors import Colors


class ShapeFill(Enum):
    """Defines how a shape may be drawn"""
    FILLED = -1
    OUTLINE = 0

class Shape(object):
    """Generic shape base class"""
    DEFAULT_THICKNESS = 2
    DEFAULT_COLOR = Colors.GREEN

    def __init__(self):
        pass

    def _draw(self, img, color, thickness):
        pass

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
