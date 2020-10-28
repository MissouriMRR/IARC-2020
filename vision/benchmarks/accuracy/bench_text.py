"""
Boat related unit tests.
"""
import os, sys

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
gggparent_dir = os.path.dirname(ggparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir, gggparent_dir]

from text.detect_words import TextDetector


IMG_FOLDER = "boat"


class AccuracyRussianWord:
    """
    Testing the text detector.
    """

    def setup(self):
        pass

    def accuracy_detector(self, color_image, depth_image):
        """
        Accuracy of detectRussianWord.

        Returns
        -------
        List[BoundingBox]
        """
        bounding_boxes = TextDetector().detect_russian_word(color_image, depth_image)

        return bounding_boxes
