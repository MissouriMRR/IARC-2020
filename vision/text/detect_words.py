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
        Detect words in given image.

        Returns
        -------
        A list of box objects that contain desired text
        """

        # filter image, b&w
        filter_image = cv2.cvtColor(color_image, cv2.COLOR_BGR2GRAY)
        # not only does tesseract basically require uint8, but apparently it has to be
        # thresholded as uint8 or tesseract will throw a fit
        filter_image = np.uint8(filter_image)
        
        # _, filter_image = cv2.threshold(filter_image, 185, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY)
        _, filter_image = cv2.threshold(filter_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        # for whatever reason pytesseract needs images in rgb form, so shape has to be (width, height, 3)
        filter_image = np.stack((filter_image,)*3, axis=2)

        # shows what the filtered image looks like
        # cv2.imshow('img', filter_image)
        # cv2.waitKey(0)
        
        ## only return boxes that have text in them
        ## eg. find a way to check if boxes are repetitive or do not contain text
        
        tessdata = pytesseract.image_to_data(filter_image, output_type=pytesseract.Output.DICT, lang="uzb_cyrl")
        
        n_boxes = len(tessdata['level'])
        box_obs = []
        contents = tessdata['text']
        # print(contents)
        for i in range(n_boxes):
            if not contents[i]:
                continue
            else:
                for j in contents[i]:
                    if j in self.text:
                        # print(contents[i])
                        (x, y, w, h) = (tessdata['left'][i], tessdata['top'][i], tessdata['width'][i], tessdata['height'][i])
                        # cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)
                        verts = [(x, y), (x + w, y), (x, y + h), (x + w, y + h)]
                        cv2.rectangle(filter_image, verts[0], verts[-1], (0, 255, 0), 2)
                        box = BoundingBox(verts, ObjectType('text'))
                        box_obs.append(box)
                        break
                        
        return box_obs


if __name__ == "__main__":
    import time
    import os
    from common import box_plotter
    
    
    
    sample_dir = os.path.join('vision_images', 'text', 'Feb29')
    sample_ims = []
    
    for filename in os.listdir(sample_dir):
        if filename.endswith(".jpg"):
            sample_ims.append(os.path.join(sample_dir, filename))
        else:
            continue
    
    times = []
    
    for i in sample_ims:
    
        color_image = cv2.imread(i)
        
        if color_image is None:
            raise FileNotFoundError("Could not read image!")

        start = time.time()


        detector = TextDetector()
        result = detector.detect_russian_word(color_image, None)
        

        times.append(time.time() - start)
        box_plotter.plot_box(result, color_image)

    print("Max: ", np.max(times))
    print("Min: ", np.min(times))
    print("Mean: ", np.mean(times))