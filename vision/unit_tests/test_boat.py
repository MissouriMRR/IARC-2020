import unittest
import os
import cv2
from boat.detectRussianWord import detect_russian_word


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
        expected = {
            'russianWord0.png': 1,
            'notboat.png': 0
        }

        # print(expected.items())

        vision_folder = 'vision' if os.path.isdir('vision') else ''

        # todo: right now it will not open the second image 'notboat.png'
        # todo: conflict in the return of the alg. needs a true/false for this. needs to return list of boxes
        for filename, expected_result in expected.items():
            image = cv2.imread(os.path.join(vision_folder, 'vision_images', 'boat', filename))
            if image is None:
                self.fail(f"Failed to read: {filename}")

            result = detect_russian_word(image)
            self.assertEqual(expected_result, result, msg=f"Failed at image {filename}")


if __name__ == '__main__':
    unittest.main()
