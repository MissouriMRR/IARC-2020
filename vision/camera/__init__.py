"""
camera __init__.

Identifies "camera" as a package in order to import submodules.
"""
import sys
import os

sys.path.append(os.path.dirname(__file__))

try:
    from template import Camera

    # conditional imports to prevent circular imports that depend on Camera
    if "realsense" not in sys.modules:
        from realsense import Realsense
    if "sim_camera" not in sys.modules:
        from sim_camera import SimCamera
    if "bag_file" not in sys.modules:
        from bag_file import BagFile

except ImportError as e:
    print(f"camera/__init__.py failed: {e}")
