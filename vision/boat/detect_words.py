"""
This program grabs text from an image and compares it with 'модули иртибот'.
It returns 'Match' if it identifies 'модули иртибот' and 'Not Match' when it doesnt.
"""
import pytesseract
import numpy as np
import cv2
import lxml.etree
import os, sys
from bounding_box import BoundingBox, ObjectType


parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]


def detect_russian_word(color_image, depth_image):
    """
    Function to detect words pulled from images
    -------

    Returns
    -------
    True if text grabbed from image matches 'модули иртибот'.
    False if not.
    """

    # filter image
    _, filter_image = cv2.threshold(np.mean(color_image, axis=2), 127, 255, cv2.THRESH_BINARY)

    # shows what the filtered image looks like
    # cv2.imshow('img', filter_image)
    # cv2.waitKey(0)

    # function from library: pytesseract to grab text from image
    # text = pytesseract.image_to_string(filter_image, lang="uzb_cyrl")
    # print(text)

    # russian_word = 'модули иртибот'
    # print(russian_word)


    ## change the output
    d = pytesseract.image_to_data(filter_image, output_type=pytesseract.Output.DICT)

    n_boxes = len(d['level'])
    box_obs = []
    for i in range(n_boxes):
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        # cv2.rectangle(color_image, (x, y), (x + w, y + h), (0, 255, 0), 2)

        verts = [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]

        box = BoundingBox(verts, ObjectType('text'))
        box_obs.append(box)

    return box_obs


if __name__ == "__main__":
    import time
    import os
    start = time.time()

    color_image = cv2.imread(os.path.join('vision_images', 'boat', 'russianWord0.png'))

    if color_image is None:
        raise FileNotFoundError("Could not read image!")

    result = detect_russian_word(color_image, None)

    print("Time:", time.time() - start)
