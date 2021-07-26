"""
common __init__.

Identifies "common" as a package in order to import submodules.
"""
import sys
import os

sys.path.append(os.path.dirname(__file__))

try:
    from import_params import import_params

except ImportError as e:
    print(f"common/__init__.py failed: {e}")
