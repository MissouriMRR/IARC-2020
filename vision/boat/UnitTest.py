import unittest
import os
import cv2
from vision.boat.detectRussianWord import detect_russian_word

class TestDetectRussianWord(unittest.TestCase):      
    def test_detect_russian(self):
        """
        Testing vision.boat.detectRussianWord

        Settings
        --------
        detectRussianWord.originalImage: PNG
            Stores image into a variable.
        detectRussianWord.text: string
            Stores text grabbed from image.

        Returns
        -------
        True if text grabbed from image matches 'модули иртибот'.
        False if not.
        """
        # Ensure 'модули иртибот' is found within image
        expected = [1, 1, 1, 1, 1,
                    1, 1, 1, 1, 1,
                    0, 0, 0, 0, 0,
                    0, 0, 0, 0, 0,]
        matched = []
        output = []
        
        vision_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        for i in vision_folder:
            image = cv2.imread(i) 
            if(detect_russian_word(image)):
                matched.append(1)
            else:
                matched.append(0)

        for i in range(0,len(matched)):
<<<<<<< HEAD
            self.assertEqual(expected[i], matched[i], msg=f"Failed at image {filename}")
=======
            if(expected[i] == matched[i]):
                output.append[1]
            else:
                output.append[0]
        
        #array used to identify which image fails or passes
        for i in range(0,len(output)):
            print("image",i, output[i])

>>>>>>> 8dc784ab4bcef5f7ecfbce456cbaf8eb7c0db325

        self.assertListEqual(list(expected), list(matched))

    
if __name__ == '__main__':
    unittest.main()
