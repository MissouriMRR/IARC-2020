"""
Helper function for OpenCV parameters.
"""

import cv2

def import_params(config: dict) -> cv2.SimpleBlobDetector_Params:
    """
    OpenCV parameter importing.

    Parameters
    ----------
    config: dict
        Desired configuration.

    Returns
    -------
    cv2.SimpleBlobDetector_Params - OpenCV blob detector parameter object.
    """
    if not isinstance(config, dict):
        raise ValueError(
            f"When importing params, config should be a dictionary, got {type(config)} instead"
        )

    params: cv2.SimpleBlobDetector_Params = cv2.SimpleBlobDetector_Params()

    for category in config:
        if "enable" not in config[category]:
            raise ValueError(f"Category '{category}' is missing an 'enable' attribute")
        category_enabled = config[category]["enable"]

        try:
            setattr(params, category, category_enabled)
        except AttributeError:
            # Not all settings have enable/disable
            pass

        if category_enabled:
            if hasattr(params, category):
                setattr(params, category, config[category]["enable"])
            for attr in config[category]:
                if hasattr(params, attr):
                    setattr(params, attr, config[category][attr])

    return params
