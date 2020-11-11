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
        # Currently non-functional
        # Idea was:
        # Find the blue rectangle around the text
        #                |
        #                V
        #      Get the contours of it
        #               |
        #               V
        #   Select only the contours with children (noise filter: only the rectangle should have child contours)
        #               |                                                   |
        #               V                                                   V
        #           Make a mask out of a contour                 Find the center of contour
        #               |                   |                               |
        #               V                   V                               |
        #        Select Edges           Select Region of plain image        |
        #              |                                   |                |
        #              V                                   |                |
        #   Run HoughLinesP on Edges                       |                |
        #              |                                   |                |
        #              V                                   |                |
        #   Use trig to find rotation of rectangle         |                |
        #                                     |            |                |
        #                                     V            V                V
        #                               Rotate region of image about center by found measure
        #                                                  |
        #                                                  V
        #                           Pass into pyTesseract, does it have our russian words in it?
        #                                    Yes                                    No
        #                                     |                                      |
        #                                     V                                      V
        #                              More trig to return the                   Were there anymore contours with children?
        #                          bounding box relative to the whole image          Yes                         No
        #                                    |                                       |                           |
        #                                    V                                       V                           V
        #                              That's it, you done         Go back through process with them         Either the image has no
        #                                                                                                    russian or it is too noisy
        #
        # This would probably be wildly unperformant, but I think it would make pytesseract understand the rotated text
        
        # the text is always in a blue rectangle. this finds the rectangle
        # remove noise, int16 to prevent negative overflow in following step
        blur_image = np.int16(cv2.GaussianBlur(color_image, (5,5), 0))
        b_image, g_image, r_image = blur_image[:,:,0], blur_image[:,:,1], blur_image[:,:,2] # separate channels
        
        isblue = np.logical_and((b_image - r_image > 120),  (b_image - g_image > 20))
        
        # make blue parts black, rest white
        mask_image = np.where(isblue, np.uint8(0), np.uint8(255))
       
        #if we have depth data, get rid of irrelevant far aways stuff like the sky
        if depth_image is not None:
            mask_image=np.where((depth_image < 8000), mask_image, np.uint8(255))

        edges = cv2.Canny(mask_image, 250, 255)
        # canny is too good at its job, soften it up a bit for houghlines and findcontours
        edges = cv2.GaussianBlur(edges, (5,5), 0)
        
        # specifically getting a 2-tier contour
        # our target is the blue rectangle surrounding the text
        # the rectangle has an inside and outside boundary, and we can use that fact to eliminate noise
        # that is, any contours that don't have child contours aren't our rectangle
        contours, hierarchy = cv2.findContours(edges, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
        
        print(hierarchy.shape)
        print(len(contours))
        
        (hierarchy[0][:][2] >= 0)
        
        print(contours[0].shape)
        
        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 250, 600, 20)
        # lines = np.where(lines[:,1] < np.pi/4
        
        
        # make it a color image again so we can draw colored lines on it
        mask_image = np.stack((mask_image,)*3, axis=2)
        
        if lines is not None:
            for i in range(lines.shape[0]):
                for x1, y1, x2, y2 in lines[i]:
                    mask_image = cv2.line(mask_image,(x1,y1),(x2,y2),(0,255,0), thickness=2)

        cv2.imshow("img", mask_image)
        cv2.waitKey(0)
        
        
        # not only does tesseract basically require uint8, but apparently it has to be
        # thresholded as uint8 or tesseract will throw a fit
        # filter_image = np.uint8(filter_image)
        # _, filter_image = cv2.threshold(filter_image, 0, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY)
        # _, filter_image = cv2.threshold(filter_image, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)  
        # for whatever reason pytesseract needs images in rgb form, so shape has to be (width, height, 3)
        # filter_image = np.stack((filter_image,)*3, axis=2)

        # shows what the filtered image looks like
        # cv2.imshow('img', filter_image)
        # cv2.waitKey(0)
        
        
        
        
        ## only return boxes that have text in them
        ## eg. find a way to check if boxes are repetitive or do not contain text
        
        tessdata = pytesseract.image_to_data(color_image, output_type=pytesseract.Output.DICT, lang="uzb_cyrl")
        
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
                        cv2.rectangle(color_image, verts[0], verts[-1], (0, 255, 0), 2)
                        box = BoundingBox(verts, ObjectType('text'))
                        box_obs.append(box)
                        break
                        
        return box_obs, mask_image


if __name__ == "__main__":
    import time
    import os
    from common import box_plotter
    
    
    
    sample_dir = os.path.join('vision_images', 'text', 'Feb29')
    sample_ims = []
    
    for filename in os.listdir(sample_dir):
        if filename.endswith(".jpg") or filename.endswith(".png"):
            sample_ims.append(os.path.join(sample_dir, filename))
        else:
            continue
    
    times = []
    
    for i in sample_ims:
    
        color_image = cv2.imread(i)
        depth_image = np.load(i.split('colorImage')[0] + 'depthImage.npy')
        
        if color_image is None:
            raise FileNotFoundError("Could not read image!")

        start = time.time()

        detector = TextDetector()
        result, mask_image = detector.detect_russian_word(color_image, depth_image)
        
        times.append(time.time() - start)
        # box_plotter.plot_box(result, mask_image)

    print("Max: ", np.max(times))
    print("Min: ", np.min(times))
    print("Mean: ", np.mean(times))