#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Copyright (c) 2021 Martin Stefanik
"""

from setuptools import find_packages, setup

from daddy import VERSION

with open('README.md') as f:
    README = f.read()

with open('requirements.txt', 'r') as f:
    REQUIRES = f.read().splitlines()

setup(
    name='daddy',
    author='Martin Stefanik',
    author_email='stefanik.mar@gmail.com',
    maintainer='Martin Stefanik',
    maintainer_email='stefanik.mar@gmail.com',
    version=VERSION,
    description='CLI tool for verification of domain name availability.',
    long_description=README,
    url='https://github.com/martinstefanik/daddy',
    license='MIT',
    py_modules=['daddy'],
    packages=find_packages(),
    python_requires='>=3.6',
    install_requires=REQUIRES,
    entry_points="""
        [console_scripts]
        daddy=daddy:daddy
    """
)
