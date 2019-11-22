"""
This is a camera parent class which different "cameras" will inherit from.

This is never to be instantiated by itself, the camera class exists purely to guarantee
certain behaviors for child classes
"""


class Camera:
    """
    Creates a camera object (only to be used by children classes)

    Parameters
    ----------
    screen_width: number
        Resolution width of the pre-recorded .bag file
    screen_height: number
        Resolution height of the pre-recorded .bag file
    frame_rate: number
        Framerate of the pre-recorded .bag file
    """
    def __init__(self, screen_width, screen_height, frame_rate):
        self.width = screen_width
        self.height = screen_height
        self.framerate = frame_rate

    """
    Guarantees that child classes have an __iter__ method
    
    Parameters
    -------------
    self: camera object
        Does not need to be passed
    """
    def __iter__(self):
        raise NotImplementedError(f"__iter__ is not implemented for {type(self)}")

    """
    Guarantees that child classes have an __iter__ method
    
    Parameters
    -------------
    self: camera object
        Does not need to be passed
    """
    def display_in_window(self):
        raise NotImplementedError(f"dilay_in_window is not implemented for {type(self)}")
