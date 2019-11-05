import unittest
from ModuleKMeans import ModuleKMeans as mkm

class TestKMeans(unittest.TestCase):

    def test_fractal(self):
        """
        Testing Fractal KMeans Display

        Test images must be put in a file called images
        """

        for pic in ["images/blocks1.jpg",
                    "images/blocks2.jpg",
                    "images/pylon.jpg"]:
            img = mkm(pic)
            img.applyKMeans(3)
            channels = [0, 1]
            img.displayFractal()

    def test_binary(self):
        """
        Testing Binary KMeans Display

        Test images must be put in a file called images
        """
        
        for pic in ["images/blocks1.jpg",
                    "images/blocks2.jpg",
                    "images/pylon.jpg"]:
            img = mkm(pic)
            img.applyKMeans(3)
            channels = [0, 1]
            img.displayBinary(channels)


if __name__ == '__main__':
    unittest.main()
