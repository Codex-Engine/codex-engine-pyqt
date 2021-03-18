#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os

from setuptools import setup


here = os.path.abspath(os.path.dirname(__file__))


DESCRIPTION = "A universal translator for serial devices."


try:
    with open(os.path.join(here, "README.md")) as f:
        LONG_DESCRIPTION = f.read()
except IOError:
    LONG_DESCRIPTION = ""


CLASSIFIERS = [
    "Programming Language :: Python :: 3.7",
    "Programming Language :: Python :: 3.8",
    "Programming Language :: Python :: 3.9",
]


setup(
    name="codex-engine-pyqt",
    version="0.0.3",
    packages=["codex"],
    install_requires=["pyserial"],
    # setup_requires=[],
    # tests_require=[],
    platforms=["any"],

    author="David Kincaid",
    author_email="dlkincaid0@gmail.com",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    classifiers=CLASSIFIERS,
    keywords=["codex", "codex engine", "serial"],
    url="https://github.com/Codex-Engine/codex-engine-pyqt"
)