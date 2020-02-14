"""
Graphical image annotator.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))

from json import load as jsonload

import cv2

from ui.colors import Colors
from ui.window import Window
from annotation.annotation import Annotation
from annotation.generate_annotation import generate_pascvalvoc_annotation_from_image_file, ANNOTATION_DEFAULT_DIR


class PascalVocAnnotator(object):
    """Annotates images in the Pascal VOC annotation format."""
    WINDOW_TITLE = 'Annotator'
    TEST_DIRECTORY = 'test_images'
    CONFIG_PATH = 'config.json'
    SUPPORTED_FILE_EXTENSIONS = ('.jpg', '.png')

    def __init__(self, path_to_image_folder=TEST_DIRECTORY):
        ## Read config
        with open(self.CONFIG_PATH, 'r') as configfile:
            data = jsonload(configfile)

        self.controls = data['controls']
        self.labels = list(data['labels'].keys())
        self.color_map = {key: value['color'] for key, value in data['labels'].items()}

        ## Read image
        if not os.path.isdir(path_to_image_folder):
            raise ValueError(f"The path \'{path_to_image_folder}\' is not a valid directory!")

        self._path_to_image_folder = path_to_image_folder
        self._paths = [os.path.join(path_to_image_folder, filename) for filename in os.listdir(self.path_to_image_folder)
                       if os.path.splitext(filename)[1] in PascalVocAnnotator.SUPPORTED_FILE_EXTENSIONS]
        self._paths.sort(key=os.path.getmtime)

        self._current_image = None

        self._saved_annotations = Annotation.load_annotations(self.path_to_image_folder, self.color_map, annotation_dir=ANNOTATION_DEFAULT_DIR)
        self._window = None
        self.tag_index = 0
        self._annotations = []
        self._annotation_in_progress = None
        self._changed = False

        self.index = 0

        self._key_events = {
            self.controls['NEXT']: self._next,
            self.controls['PREV']: self._prev,
            self.controls['CHANGE_TAG']: self._next_tag,
            self.controls['UNDO']: self._undo,
            self.controls['CLEAR']: self._clear
        }

        ## Print controls
        print("Controls")
        for key, value in self._key_events.items():
            print(f"{value.__name__}: {key}")

        print()

    def __enter__(self):
        self._window = Window(PascalVocAnnotator.WINDOW_TITLE, cv2.WND_PROP_FULLSCREEN).__enter__()

        self._window.set_property(cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        self._window.set_mouse_callback(self.on_mouse_event)

        return self

    def __exit__(self, *params):
        self.index += 1

        if self._window is not None:
            self._window.__exit__()

    @property
    def path_to_image_folder(self):
        return self._path_to_image_folder

    @property
    def annotation_dir(self):
        return ANNOTATION_DEFAULT_DIR

    @property
    def paths(self):
        return self._paths

    @property
    def index(self):
        return self._index

    @property
    def current_path(self):
        return self.paths[self.index]

    @property
    def current_image(self):
        return self._current_image

    @current_image.setter
    def current_image(self, value):
        assert value is not None, 'Cannot read the image at "{}"!'.format(self.current_path)
        self._current_image = value

    def _next(self):
        self.index += 1

    def _prev(self):
        self.index -= 1

    def _next_tag(self):
        self.tag_index += 1

    def _clear(self):
        if self._annotations:
            self._annotations.clear()
            self._changed = True

    def _undo(self):
        if self._annotations:
            self._annotations.pop(0)
            self._changed = True

    def _remove_annotation_file_when_empty(self):
        if hasattr(self, '_index'):
            annotation_file_path = os.path.join(self.path_to_image_folder, self.annotation_dir, os.path.basename(os.path.splitext(self.current_path)[0]) + '.xml')
            if (not self._annotations) and os.path.isfile(annotation_file_path):
                os.remove(annotation_file_path)

    @index.setter
    def index(self, value):
        if self.current_image is not None and (self._annotations or self._changed):
            current_labels = [annotation.label for annotation in self._annotations]
            generate_pascvalvoc_annotation_from_image_file(os.path.abspath(self.current_path), current_labels, self._annotations, self.annotation_dir, True)
            self._saved_annotations[os.path.basename(self.current_path)] = self._annotations.copy()

        self._remove_annotation_file_when_empty()

        value = value % len(self._paths)
        self._index = value
        current_path = self._paths[self.index]
        img = cv2.imread(current_path)
        self.current_image = img

        key = os.path.basename(current_path)
        if key in self._saved_annotations:
            self._annotations = self._saved_annotations[key]
        else:
            self._annotations = []

        self._changed = False

    @property
    def tag_index(self):
        return self._tag_index

    @tag_index.setter
    def tag_index(self, value):
        self._tag_index = value % len(self.labels)

    @property
    def current_color(self):
        return self.color_map[self.labels[self.tag_index]]

    @property
    def tag(self):
        return self.labels[self.tag_index]

    def show_tag(self, img):
        """
        Display tag in use on top of screen.
        """
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        thickness = 2
        margin = 5
        outline_thickness = 5

        text = f'Active tag: {self.tag}'
        (_, text_h), __ = cv2.getTextSize(text, font, font_scale, thickness)
        origin = (margin, margin + text_h)
        cv2.putText(img, text, origin, font, font_scale, Colors.BLACK.value,
                    thickness+outline_thickness)
        cv2.putText(img, text, origin, font, font_scale, self.current_color, thickness)

    def update(self):
        """
        Refresh the whole screen and process actions.
        """
        frame = self._current_image.copy()

        for key, event in self._key_events.items():
            if self._window.was_key_pressed(key):
                event()

        for annotation in self._annotations:
            annotation.draw(frame)

        if self._annotation_in_progress is not None:
            self._annotation_in_progress.draw(frame)

        self.show_tag(frame)

        self._window.draw(frame)
        return not self._window.should_quit

    def on_mouse_event(self, event, x, y, flags, params):
        """
        Process mouse press events.
        """
        for annotation in self._annotations:
            processed = annotation.on_mouse_event(event, x, y, flags, params)

            if processed:
                self._changed = True
                return

        if event == cv2.EVENT_LBUTTONDOWN and (not self._annotation_in_progress):
            self._annotation_in_progress = Annotation(x, y, self.current_color, self.tag)

        elif event == cv2.EVENT_LBUTTONUP and self._annotation_in_progress:
            self._annotations.insert(0, self._annotation_in_progress)
            self._annotation_in_progress = None

        elif event == cv2.EVENT_MOUSEMOVE and self._annotation_in_progress:
            self._annotation_in_progress.box.w = abs(x - self._annotation_in_progress.box.x)
            self._annotation_in_progress.box.h = abs(y - self._annotation_in_progress.box.y)

        self._changed |= bool(self._annotation_in_progress)


if __name__ == '__main__':
    DATASET_PATH = os.path.join("..", "..", "vision_images", "obstacle")

    with PascalVocAnnotator(DATASET_PATH) as annotator:
        while annotator.update():
            pass
