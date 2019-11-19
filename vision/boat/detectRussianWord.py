"""
This program grabs text from an image and compares it with 'модули иртибот'.
It returns 'Match' if it identifies 'модули иртибот' and 'Not Match' when it doesnt.
"""
from pytesseract import Output
import pytesseract
import numpy as np
import cv2
import time

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
    (thresh, filterImage) = cv2.threshold(np.mean(imagePNG, axis=2), 127, 255, cv2.THRESH_BINARY)
    
    #shows what the filtered image looks like
    #cv2.imshow('img', filterImage)
    #cv2.waitKey(0)

    #function from library: pytesseract to grab text from image
    text = pytesseract.image_to_string(filterImage, lang="rus")
    #print(text)
    
    russianWord = 'модули иртибот'
    #print(russianWord)
    
    if (text == russianWord):
        #print("Match")
        return True
    else :
        #print("Not Match")
        return False

if __name__== "__main__":
    import os
    start = time.time()
    originalImage = cv2.imread("imagePNG")
    detect_russian_word(originalImage)
    end = time.time()
    print(end - start)