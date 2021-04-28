"""
Testing vision.util.import_params.
"""
import unittest
import os, sys

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir]

from copy import deepcopy

try:
    from vision.common.import_params import import_params
except ImportError:
    from common.import_params import import_params


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
            whether each configuration matches the expected value
        """
        sample_config = {
            "filterByArea": {"enable": True, "minArea": 200},
            "filterByColor": {"enable": False, "blobColor": 100},
        }
        params = import_params(sample_config)

        for category, settings in sample_config.items():
            with self.subTest(i=category):
                enabled = sample_config[category]["enable"]

                for param, value in settings.items():
                    if param == "enable":
                        self.assertEqual(
                            getattr(params, category),
                            value,
                            msg=f"Expected attribute '{category}' to have value '{value}', got '{getattr(params, category)}' instead",
                        )

                    elif enabled:
                        self.assertEqual(
                            getattr(params, param),
                            value,
                            msg=f"Expected attribute '{param}' to have value '{value}', got '{getattr(params, param)}' instead",
                        )

        ## Ensure does not modify original parameter
        config_original = {
            "filterByArea": {"enable": True, "minArea": 200},
            "filterByColor": {"enable": False, "blobColor": 100},
        }

        config_parameter = deepcopy(config_original)

        import_params(config_parameter)

        self.assertDictEqual(config_original, config_parameter)


if __name__ == "__main__":
    unittest.main()
