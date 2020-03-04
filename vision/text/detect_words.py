"""
This program grabs text from an image and compares it with 'модули иртибот'.
It returns 'Match' if it identifies 'модули иртибот' and 'Not Match' when it doesnt.
"""
import pytesseract
import numpy as np
import cv2
import os, sys


parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

from bounding_box import BoundingBox, ObjectType

class TextDetector:

    def __init__(self):
        self.text = 'модулииртибот'

    def detect_russian_word(self, color_image, depth_image):
        """
        Function to detect words pulled from images
        -------

        Returns
        -------
        A list of box objects that contain desired text
        """

        # filter image
        _, filter_image = cv2.threshold(np.mean(color_image, axis=2), 185, 255, cv2.THRESH_BINARY)

        # shows what the filtered image looks like
        # cv2.imshow('img', filter_image)
        # cv2.waitKey(0)


        ## only return boxes that have text in them
        ## eg. find a way to check if boxes are repetitive or do not contain text
        print(filter_image)
        d = pytesseract.image_to_data(filter_image, output_type=pytesseract.Output.DICT, lang="uzb_cyrl")

        n_boxes = len(d['level'])
        box_obs = []
        contents = d['text']
        # print(contents)
        for i in range(n_boxes):
            if not contents[i]:
                continue
            else:
                for j in contents[i]:
                    if j in self.text:
                        # print(contents[i])
                        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
                        # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        verts = [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]
                        cv2.rectangle(filter_image, verts[0], verts[-1], (0, 255, 0), 2)
                        box = BoundingBox(verts, ObjectType('text'))
                        box_obs.append(box)
                        break

        # cv2.imshow('img', filter_image)
        # cv2.waitKey(0)

        return box_obs


if __name__ == "__main__":
    import time
    import os
    start = time.time()

    color_image = cv2.imread(os.path.join('vision_images', 'text', '2020-02-23.png'))

    if color_image is None:
        raise FileNotFoundError("Could not read image!")

    detector = TextDetector()
    result = detector.detect_russian_word(color_image, None)
    print(result)

    print("Time:", time.time() - start)
