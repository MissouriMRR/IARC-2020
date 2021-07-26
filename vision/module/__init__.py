"""
module __init__.

Identifies "module" as a package in order to import submodules.
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

try:
    from location import ModuleLocation
    from region_of_interest import get_region_of_interest
    from module_bounding import get_module_bounds
    from module_orientation import get_module_orientation, get_module_roll
    from module_depth import get_module_depth

except ImportError as e:
    print(f"module/__init__.py failed: {e}")
