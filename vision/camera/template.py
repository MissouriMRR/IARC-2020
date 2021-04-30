"""
This is a camera parent class which different "cameras" will inherit from.

This is never to be instantiated by itself, the camera class exists purely to guarantee
certain behaviors for child classes
"""


class Camera:
    def __init__(self, screen_width: int, screen_height: int, frame_rate: int):
        """
        Creates a camera object (only to be used by children classes)

        Parameters
        ----------
        screen_width: int
            Resolution width of the stream
        screen_height: int
            Resolution height of the stream
        frame_rate: int
            Framerate of the stream
        """
        self.width = screen_width
        self.height = screen_height
        self.framerate = frame_rate

    def __iter__(self):
        """
        Guarantees that child classes have an __iter__ method

        Returns
        -------------
        depth frame: numpy array
            as implemented in child classes
        color frame: numpy array
            as implemented in child classes
        """
        raise NotImplementedError(f"__iter__ is not implemented for {type(self)}")

    def display_in_window(self):
        """
        Guarantees that child classes have the display_in_window method
        """
        raise NotImplementedError(
            f"display_in_window is not implemented for {type(self)}"
        )
