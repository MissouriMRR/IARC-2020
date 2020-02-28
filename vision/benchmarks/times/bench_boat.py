"""
Boat related unit tests.
"""
import os, sys
parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

import cv2

from boat.detect_words import detect_russian_word


class TimeDetectRussianWord:
    """
    Testing the text detector.
    """
    def setup(self):
        """
        Load images.
        """
        prefix = '' if os.path.isdir("times") else '..'

        ## Load images
        img_folder = os.path.join(prefix, '..', 'vision_images', 'boat')

        self.PARAMETERS = {}
        for filename in os.listdir(img_folder):
            if filename[-4:] not in ['.png', '.jpg']:
                continue

            img_path = os.path.join(img_folder, os.fsdecode(filename))

            image = cv2.imread(img_path)

            self.PARAMETERS.update({filename: [image, None]})

    def time_detector(self, color_image, depth_image):
        """
        Timing detectRussianWord.
        """
        detect_russian_word(color_image, depth_image)
