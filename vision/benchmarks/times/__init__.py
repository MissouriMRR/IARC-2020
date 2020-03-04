"""
benchmarks/time __init__.
"""
import sys
import os
sys.path.append(os.path.dirname(__file__))

try:
    modules = []

    for filename in os.listdir('times'):
        if filename is 'runall.py':
            continue

        if filename[:5] != 'bench' or filename[-3:] != '.py':
            continue
        print(filename)

        modules.append(__import__(f'{filename[:-3]}'))

except ImportError as e:
    print(f"benchmarks/time/__init__.py failed: {e}")
