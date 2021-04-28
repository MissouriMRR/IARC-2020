"""
ui window.
"""
import cv2


class Window(object):
    """Abstracts OpenCV's high-level QT functionality."""

    QUIT_KEY = "q"
    QUIT_KEY2 = ""

    def __init__(self, title="", flags=None, quit_key=QUIT_KEY, quit_key2=QUIT_KEY2):
        self.title = title
        self._flags = [] if flags is None else [flags]
        self.destroyed = False
        self.should_quit = False
        self._pipelines = []
        self.quit_key = quit_key
        self.quit_key2 = quit_key2
        self._unprocessed_keys = {}

        cv2.namedWindow(title, *self._flags)

    def __enter__(self):
        return self

    def __exit__(self, *params):
        if not self.destroyed:
            cv2.destroyWindow(self.title)

        self.destroyed = True

    def set_mouse_callback(self, callback):
        cv2.setMouseCallback(self.title, callback)

    def set_property(self, key, value):
        cv2.setWindowProperty(self.title, key, value)

    def get_key(self):
        key = chr(cv2.waitKey(int(2)) & 0xFF)

        if key == self.quit_key or key == self.quit_key2:
            self.should_quit = True

        self._unprocessed_keys[key] = True

        return key

    def was_key_pressed(self, key, processed=True):
        result = key in self._unprocessed_keys

        if processed and result:
            del self._unprocessed_keys[key]

        return result

    def draw(self, img):
        for pipeline in self._pipelines:
            pipeline.update()
            img = pipeline.output_image

        cv2.imshow(self.title, img)
        self.get_key()
