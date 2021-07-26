"""
pylon __init__.

Identifies "pylon" as a package in order to import submodules.
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

try:
    from detect_pylon import detect_red

except ImportError as e:
    print(f"pylon/__init__.py failed: {e}")
