"""
Camera __init__.
"""
import sys
import os

sys.path.append(os.path.dirname(__file__))

try:
    from realsense import Realsense
    from sim_camera import SimCamera
    from bag_file import BagFile

except ImportError as e:
    print(f"camera/__init__.py failed: {e}")
