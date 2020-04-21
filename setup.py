#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pathlib

from setuptools import find_packages, setup

here = pathlib.Path(__file__).parent
long_description = here.joinpath("README.md").read_text()

setup(
    name="wemo",
    version="0.1.0",
    description="Collect data from and control WEMO Insight devices",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Simon Bowly",
    author_email="simon.bowly@gmail.com",
    python_requires=">=3.7",
    packages=find_packages(exclude=["tests", "*.tests", "*.tests.*", "tests.*"]),
    install_requires=["click", "requests"],
    entry_points={"console_scripts": ["wemo=wemo.cli:cli"]},
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
)
