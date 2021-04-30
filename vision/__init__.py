"""
vision __init__.

Identifies "vision" as a package in order to import submodules.
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

try:
    from bounding_box import ObjectType, BoundingBox

    from interface import Environment

    from failure_flags import FailureFlags
    from failure_flags import ModuleDetectionFlags
    from failure_flags import TextDetectionFlags
    from failure_flags import ObstacleDetectionFlags

    from pipeline import arange
    from pipeline import init_vision
    from pipeline import Pipeline

except ImportError as e:
    print(f"vision/__init__.py failed: {e}")
