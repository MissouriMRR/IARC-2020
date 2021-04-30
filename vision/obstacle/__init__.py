"""
obstacle __init__.

Identifies "obstacle" as a package in order to import submodules.
"""

import sys
import os

sys.path.append(os.path.dirname(__file__))

try:
    from obstacle_finder import ObstacleFinder
    from obstacle_tracker import Obstacle, ObstacleTracker

except ImportError as e:
    print(f"obstacle/__init__.py failed: {e}")
