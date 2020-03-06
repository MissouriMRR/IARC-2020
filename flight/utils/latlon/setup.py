#!/usr/bin/env python
# -*- coding: us-ascii -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
"""Examples:
        setup.py sdist
        setup.py bdist_wininst
"""

from distutils.core import setup

long_description = open("README.md", "r").read()

setup(name='latlon3',
    version='1.0.3',
    description='Methods for representing geographic coordinates',
    url='https://github.com/search5/latlon',
    license='GNU General Public License v3 (GPLv3)',
    scripts=['__init__.py', 'latlon.py'],
    author="Lee Ji-ho",
    author_email="search5@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=['six',],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Topic ::Scientific/Engineering"
    ])
