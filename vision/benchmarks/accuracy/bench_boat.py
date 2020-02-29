"""
Boat related unit tests.
"""
import os, sys

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

from boat.detect_words import detect_russian_word


IMG_FOLDER = 'boat'

class AccuracyRussianWord:
    """
    Testing the text detector.
    """
    def setup():
        pass

    def accuracy_detector(self, color_image, depth_image):
        """
        Accuracy of detectRussianWord.

        Returns
        -------
        List[BoundingBox]
        """
        bounding_boxes = detect_russian_word(color_image, depth_image)

        return bounding_boxes
