import unittest
from ModuleInFrame import ModuleInFrame as mif

class TestModuleInFrame(unittest.TestCase):
    def test_ModuleInFrame(self):
        """
        Testing ModuleInFrame
        
        Settings
        --------
        None

        Returns
        -------
        ndarray[bool] which images the module was detected in
        """

        results = []
        for pic in ["D_Img1.jpg", "D_Img2.jpg", "D_Img3.jpg"]:
            results.append(mif(pic))
        return results

if __name__ == '__main__':
        unittest.main()