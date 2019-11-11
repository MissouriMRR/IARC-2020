"""
Image annotator.
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))

import xml.etree.ElementTree as ET
from enum import Enum

import cv2
import numpy as np

from colors import Colors
from ui.Window import Window
from geometry.ResizableBox import ResizableBox
from tools.GeneratePascalVocAnnotations import generate_pascvalvoc_annotation_from_image_file, ANNOTATION_DEFAULT_DIR


class Annotation(object):
    '''Represents a particular object annoation'''
    detector = None

    def __init__(self, x, y, color, label, w=1, h=1):
        self._resizable_box = ResizableBox(x, y, w, h)
        self.color = color
        self._label = label
        self._tracker = None
        self._detector = None

    @property
    def box(self):
        return self._resizable_box

    @property
    def label(self):
        return self._label

    def on_mouse_event(self, event, x, y, flags, params):
        self._resizable_box.on_mouse_event(event, x, y, flags, params)
        return self._resizable_box.changed

    def scale_by(self, scale):
        bounds = self.box.scale_by(scale)
        return Annotation(bounds.x, bounds.y, self.color, self.label, w=bounds.w, h=bounds.h)

    def draw(self, img):
        self._resizable_box.draw(img, self.color)

    @staticmethod
    def make_guess(img, *kwargs):
        return []#annotations

    @staticmethod
    def parse_annotation(path, color_map):    
        tree = ET.parse(path)
        root = tree.getroot()
        annotations = []

        path = root.find('path').find('value').text

        for obj in root.findall('object'):
            label = obj.find('name').text
            bbox = obj.find('bndbox')
            x, y, x1, y1 = (int(bbox.find('xmin').text), int(bbox.find('ymin').text), int(bbox.find('xmax').text), int(bbox.find('ymax').text))

            color = color_map[label]
            annotations.append(Annotation(x, y, color, label, x1-x, y1-y))
    
        return annotations, path

    @staticmethod
    def load_annotations(path_to_image_folder, color_map, annotation_dir=ANNOTATION_DEFAULT_DIR):
        color_map = color_map.value if hasattr(color_map, 'value') else color_map
        path = os.path.join(path_to_image_folder, annotation_dir)
        saved_annotations = {}

        if os.path.isdir(path):
            for file in os.listdir(path):
                annotation_file_path = os.path.join(path, file)
                annotations, key = Annotation.parse_annotation(annotation_file_path, color_map)
                saved_annotations[key] = annotations

        return saved_annotations


class ColorMaps(Enum):
    FORTNITE = [(200, 150, 120), (0, 200, 255), (255, 200, 0)]


class ObjectLabels(Enum):
    FORTNITE = ['player', 'ammo box', 'chest']


class PascalVocAnnotator(object):
    """Annotates images in the Pascal VOC annotation format."""
    WINDOW_TITLE = 'Annotator'
    TEST_DIRECTORY = 'test_images'
    SUPPORTED_FILE_EXTENSIONS = ('.jpg', '.png')
    ENABLE_AI_ASSISTED_ANNOTATIONS = True

    NEXT_KEY = 'n'
    PREV_KEY = 'p'
    CLEAR_KEY = 'c'
    UNDO_KEY = 'u'
    CHANGE_OBJECT_TAG = 't'

    def __init__(self, path_to_image_folder=TEST_DIRECTORY, obj_labels=ObjectLabels.FORTNITE, color_map=ColorMaps.FORTNITE):
        if not os.path.isdir(path_to_image_folder):
            raise ValueError('The path "{}" is not a valid directory!'.format(path_to_image_folder))

        self._colors = color_map if not hasattr(color_map, 'value') else color_map.value
        self._obj_labels = obj_labels if not hasattr(obj_labels, 'value') else obj_labels.value
        
        assert len(self._colors) >= len(self._obj_labels), 'Not enough colors for the number of tags available!'

        self._path_to_image_folder = path_to_image_folder
        self._paths = [os.path.join(path_to_image_folder, file) for file in os.listdir(self.path_to_image_folder) 
                       if os.path.splitext(file)[1] in PascalVocAnnotator.SUPPORTED_FILE_EXTENSIONS]
        self._paths.sort(key = lambda path: os.path.getmtime(path))
        self._num_paths = len(self._paths)
        self._current_image = None

        self._num_labels = len(self._obj_labels)
        self._color_map = {label: self._colors[i] for i, label in enumerate(self._obj_labels)}
        self._saved_annotations = Annotation.load_annotations(self.path_to_image_folder, self._color_map)
        self._window = None
        self.tag_index = 0
        self._annotations = []
        self._annotation_in_progress = None
        self._changed = False
        self._can_guess = True

        self.index = 0

        self._key_events = {
            PascalVocAnnotator.NEXT_KEY: self._next,
            PascalVocAnnotator.PREV_KEY: self._prev,
            PascalVocAnnotator.CHANGE_OBJECT_TAG: self._next_tag,
            PascalVocAnnotator.UNDO_KEY: self._undo,
            PascalVocAnnotator.CLEAR_KEY: self._clear
        }
        
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
    def current_image(self):
        return self._current_image

    @property
    def current_path(self):
        return self.paths[self.index]

    @property
    def current_color(self):

        color = self._current_color.value if hasattr(self._current_color, 'value') else self._current_color
        return color

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

        if value < 0:
            value = self._num_paths - 1

        value = value % self._num_paths
        self._index = value
        current_path = self._paths[self.index]
        img = cv2.imread(current_path)
        self.current_image = img

        key = os.path.basename(current_path)
        if key in self._saved_annotations:
            self._annotations = self._saved_annotations[key]
        else:
            self._annotations = []
            
            if self._can_guess and PascalVocAnnotator.ENABLE_AI_ASSISTED_ANNOTATIONS:
                self._annotations = Annotation.make_guess(img, self._color_map)

        self._changed = False

    @property
    def tag_index(self):
        return self._tag_index

    @tag_index.setter
    def tag_index(self, value):
        if value < 0:
            value = self._num_labels - 1

        self._tag_index = value % self._num_labels
        self._current_color = self._colors[self.tag_index]

    @property
    def tag(self):
        return self._obj_labels[self.tag_index]

    def show_tag(self, img):
        font = cv2.FONT_HERSHEY_SIMPLEX
        font_scale = 1
        thickness = 2
        margin = 5
        outline_thickness = 5
        color = self.current_color

        text = 'Active tag: {}'.format(self.tag)
        size, baseline = cv2.getTextSize(text, font, font_scale, thickness)
        text_w, text_h = size
        origin = (margin, margin + text_h)
        cv2.putText(img, text, origin, font, font_scale, Colors.BLACK.value, thickness+outline_thickness)
        cv2.putText(img, text, origin, font, font_scale, color, thickness)

    def update(self):
        check_key_press = lambda key: self._window.was_key_pressed(key)
        frame = self._current_image.copy()

        for key, event in self._key_events.items():
            if check_key_press(key):
                event()

        for annotation in self._annotations:
            annotation.draw(frame)

        if self._annotation_in_progress is not None:
            self._annotation_in_progress.draw(frame)
        
        self.show_tag(frame)

        self._window.draw(frame)
        return not self._window.should_quit

    def on_mouse_event(self, event, x, y, flags, params):
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

        if self._annotation_in_progress:
            self._changed = True


if __name__ == '__main__':
    DATASET_PATH = os.path.join("..", "vision_images", "blob")

    with PascalVocAnnotator(DATASET_PATH) as annotator:
        while annotator.update():
            pass
