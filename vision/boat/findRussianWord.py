from PIL import Image
import pytesseract
from pytesseract import Output
import numpy as np
import cv2
import time

def detectRussianWord(imagePNG):

    originalImage = cv2.imread(imagePNG)
    #grayImage = cv2.cvtColor(originalImage, cv2.COLOR_BGR2GRAY)
    
    (thresh, filterImage) = cv2.threshold(originalImage, 127, 255, cv2.THRESH_BINARY)
    
    #cv2.imshow('img', grayImage)
    #cv2.waitKey(0)



    text = pytesseract.image_to_string(filterImage, lang="rus")  #Specify language to look after!
    print(text)
    russianWord = 'модули иртибот'
    print(russianWord)
    if (text == russianWord):
        print("Match")
    else :
        print("Not Match")



if __name__== "__main__":
    start = time.time()
    detectRussianWord("resources/russianWord1.png")
    end = time.time()
    print(end - start)