"""
The annotation object.
"""
import os
import lxml.etree as ET

from ui.geometry import ResizableBox


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
    def load_annotations(path_to_image_folder, color_map, annotation_dir):
        """
        Load previously made annotations from file.
        """
        path = os.path.join(path_to_image_folder, annotation_dir)
        saved_annotations = {}

        if os.path.isdir(path):
            for file in os.listdir(path):
                annotation_file_path = os.path.join(path, file)
                annotations, key = Annotation.parse_annotation(annotation_file_path, color_map)
                saved_annotations[key] = annotations

        return saved_annotations
