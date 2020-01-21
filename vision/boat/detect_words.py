"""
This program grabs text from an image and compares it with 'модули иртибот'.
It returns 'Match' if it identifies 'модули иртибот' and 'Not Match' when it doesnt.
"""
import pytesseract
import numpy as np
import cv2


def detect_russian_word(imagePNG):
    """
    Function to detect words pulled from images
    -------

    Returns
    -------
    True if text grabbed from image matches 'модули иртибот'.
    False if not.
    """

    #filter image
    _, filterImage = cv2.threshold(np.mean(imagePNG, axis=2), 127, 255, cv2.THRESH_BINARY)

    #shows what the filtered image looks like
    #cv2.imshow('img', filterImage)
    #cv2.waitKey(0)

    #function from library: pytesseract to grab text from image
    text = pytesseract.image_to_string(filterImage, lang="rus")
    #print(text)

    russianWord = 'модули иртибот'
    #print(russianWord)

    """ Debug
    d = pytesseract.image_to_data(filterImage, output_type=Output.DICT)
    n_boxes = len(d['level'])
    for i in range(n_boxes):
        (x, y, w, h) = (d['left'][i], d['top'][i], d['width'][i], d['height'][i])
        cv2.rectangle(imagePNG, (x, y), (x + w, y + h), (0, 255, 0), 2)

    cv2.imshow('img', imagePNG)
    cv2.waitKey(0)
    """

    return text == russianWord


if __name__ == "__main__":
    import time
    import os
    start = time.time()

    originalImage = cv2.imread(os.path.join('vision_images', 'boat', 'russianWord0.png'))

    if originalImage is None:
        raise FileNotFoundError("Could not read image!")

    result = detect_russian_word(originalImage)

    print("Result:", result)
    print("Time:", time.time() - start)
