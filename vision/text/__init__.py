"""
text __init__.

Identifies "text" as a package in order to import submodules.
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

try:
    from detect_words import TextDetector

except ImportError as e:
    print(f"text/__init__.py failed: {e}")
