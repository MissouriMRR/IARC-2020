import unittest
import os
import sys
import cv2
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from vision.blob.blobfind import import_params
except ImportError:
    from blob.blobfind import import_params

class TestParamsImport(unittest.TestCase):
    def test_params_import(self):
        """
        Tests importing params from json

        Settings
        --------
        sample_config: dict{string: dict{string: value}}
            config for setting params for SimpleBlobDetector

        Returns
        -------
        list[bool]
            whether the expected number of blobs in each image equals the detected number of blobs
        """
        vision_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        sample_config = {
            "filterByArea": {
                "enable": True,
                "minArea": 200
            },
            "filterByColor": {
                "enable": False,
                "blobColor": 100
            }
        }
        params = import_params(sample_config)

        for category, settings in sample_config.items():
            self.assertTrue('enable' in sample_config[category], msg=f"Expected key 'enable' in category {category}")
            enabled = sample_config[category]['enable']
            for param, value in settings.items():
                with self.subTest(i=category):
                    if hasattr(params, param) and enabled:
                        self.assertEqual(getattr(params, param), value, msg=f"Expected attribute '{param}' to have value '{value}', got '{getattr(params, param)}' instead")

if __name__ == '__main__':
    unittest.main()
