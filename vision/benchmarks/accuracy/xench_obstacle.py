"""
Obstacle detector unit tests.
"""
import os, sys

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import json
import lxml.etree

import numpy as np
import cv2

from vision.obstacle.obstacle_finder import ObstacleFinder
from vision.util.import_params import import_params


class AccuracyObstacle:
    """
    Measuring accuracy of obstacle detection.
    """
    def accuracy_find(self):
        """
        Test accuracy of obstacle finder via custom Annotations w/ blob_annotator tool.
        """
        THRESHOLD = 5

        prefix = 'vision' if os.path.isdir("vision") else ''
        img_folder = os.path.join(prefix, 'vision_images', 'obstacle')
        annotation_folder = os.path.join(img_folder, 'Annotations')

        ## Read annotations
        if not os.path.isdir(annotation_folder):
            print(f"No annotation folder found! -- {annotation_folder}")
            return

        annotations = {filename: lxml.etree.parse(os.path.join(annotation_folder, filename)).getroot() for filename in os.listdir(annotation_folder)}

        print(f"Found {len(annotations)} annotations in vision_images/obstacle!")

        ## Check accuracy of obstacle detector
        config_filename = os.path.join(prefix, 'obstacle', 'config.json')
        with open(config_filename, 'r') as config_file:
            raw_config = json.load(config_file)

        config = import_params(raw_config)

        for _, annotation in annotations.items():
            filename = annotation.find('path').find('value').text

            with self.subTest(i=filename):
                img_path = os.path.join(img_folder, filename)
                image = cv2.imread(img_path)

                assert image.shape, f"Failed to read {img_path}!"

                bounding_boxes = ObstacleFinder(params=config).find(image)

                accuracy = 0

                for value in annotation.findall('object'):
                    annotation_bounding_box = value.find('bndbox')

                    ax1, ay1, ax2, ay2 = [int(annotation_bounding_box.find(param).text) for param in ['xmin', 'ymin', 'xmax', 'ymax']]

                    for bounding_box in bounding_boxes:
                        ## Get x's and y's from bounding box
                        X, Y = [], []
                        for x, y in bounding_box.vertices:
                            X.append(x)
                            Y.append(y)
                        X, Y = np.unique(X), np.unique(Y)
                        bx1, by1, bx2, by2 = min(X), min(Y), max(X), max(Y)

                        ## see if bx1, by1,... within +/- threshold of each ax1, ...

                        x1_close = bx1 - THRESHOLD <= ax1 <= bx1 + THRESHOLD
                        y1_close = by1 - THRESHOLD <= ay1 <= by1 + THRESHOLD
                        x2_close = bx2 - THRESHOLD <= ax2 <= bx2 + THRESHOLD
                        y2_close = by2 - THRESHOLD <= ay2 <= by2 + THRESHOLD

                        if all((x1_close, y1_close, x2_close, y2_close)):
                            accuracy += 1

            accuracy /= len(annotation.findall('object'))
            print(f"{filename}: {accuracy * 100:.2f}%")
