"""
This program grabs text from an image and compares it with 'модули иртибот'.
It returns 'Match' if it identifies 'модули иртибот' and 'Not Match' when it doesnt.
"""
import pytesseract
import numpy as np
import cv2

import lxml.etree
import os, sys


parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

from bounding_box import BoundingBox
from bounding_box import ObjectType


def test_annotation_accuracy():  # TODO maybe this should be a benchmark?
    """
    Test accuracy of blob finder via custom Annotations w/ blob_annotator tool.
    """
    THRESHOLD = 5

    prefix = 'vision' if os.path.isdir("vision") else ''
    img_folder = os.path.join(prefix, 'vision_images', 'boat')
    annotation_folder = os.path.join(img_folder, 'Annotations')

    # Read annotations
    if not os.path.isdir(annotation_folder):
        print(f"No annotation folder found! -- {annotation_folder}")
        return

    annotations = {filename: lxml.etree.parse(os.path.join(annotation_folder, filename)).getroot() for filename in os.listdir(annotation_folder)}

    print(f"Found {len(annotations)} annotations in vision_images/blob!")

    for _, annotation in annotations.items():
        filename = annotation.find('path').find('value').text
        img_path = os.path.join(img_folder, filename)
        image = cv2.imread(img_path)

        assert image.shape, f"Failed to read {img_path}!"

        bounding_boxes = detect_russian_word(image)

        accuracy = 0

        for value in annotation.findall('object'):
            annotation_bounding_box = value.find('bndbox')

            ax1, ay1, ax2, ay2 = [int(annotation_bounding_box.find(param).text) for param in ['xmin', 'ymin', 'xmax', 'ymax']]

            for bounding_box in bounding_boxes:
                ## Get x's and y's from bounding box
                X, Y, Z = [], [], []
                for x, y, z in bounding_box.vertices:
                    X.append(x)
                    Y.append(y)
                    Z.append(z)
                X, Y = np.unique(X), np.unique(Y)
                bx1, by1, bx2, by2 = min(X), min(Y), max(X), max(Y)

                ## see if bx1, by1,... within +/- threshold of each ax1, ...

                x1_close = bx1 - THRESHOLD <= ax1 <= bx1 + THRESHOLD
                y1_close = by1 - THRESHOLD <= ay1 <= by1 + THRESHOLD
                x2_close = bx2 - THRESHOLD <= ax2 <= bx2 + THRESHOLD
                y2_close = by2 - THRESHOLD <= ay2 <= by2 + THRESHOLD

                if all((x1_close, y1_close, x2_close, y2_close)):
                    accuracy += 1

        ## TODO split this up into true positives and false negatives -- detector not guessing more than should
        accuracy /= len(annotation.findall('object'))
        print(f"{filename}: {accuracy * 100:.2f}%")


def detect_russian_word(imagePNG):
    """
    Function to detect words pulled from images
    -------

    Returns
    -------
    True if text grabbed from image matches 'модули иртибот'.
    False if not.
    """

    # filter image
    _, filter_image = cv2.threshold(np.mean(imagePNG, axis=2), 127, 255, cv2.THRESH_BINARY)

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
    print(d)
    n_boxes = len(d['level'])
    box_obs = []
    for i in range(n_boxes):
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        cv2.rectangle(imagePNG, (x, y), (x + w, y + h), (0, 255, 0), 2)

        verts = [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]

        box = BoundingBox(verts, ObjectType('text'))
        box_obs.append(box)

    return box_obs


if __name__ == "__main__":
    import time
    import os
    start = time.time()

    originalImage = cv2.imread(os.path.join('vision_images', 'boat', 'russianWord0.png'))

    if originalImage is None:
        raise FileNotFoundError("Could not read image!")

    result = detect_russian_word(originalImage)

    print("Time:", time.time() - start)
