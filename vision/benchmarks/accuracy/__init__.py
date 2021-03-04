"""
benchmarks/accuracy __init__.
"""
import __init__

import os, sys

parent_dir = os.path.dirname(os.path.abspath(__file__))
gparent_dir = os.path.dirname(parent_dir)
ggparent_dir = os.path.dirname(gparent_dir)
gggparent_dir = os.path.dirname(ggparent_dir)
sys.path += [parent_dir, gparent_dir, ggparent_dir, gggparent_dir]

try:
    modules = []

    for filename in os.listdir("vision/benchmarks/accuracy"):
        if filename == "runall.py":
            continue

        if filename[:5] != "bench" or filename[-3:] != ".py":
            continue

        modules.append(__import__(f"{filename[:-3]}"))

except ImportError as e:
    print(f"benchmarks/accuracy/__init__.py failed: {e}")
