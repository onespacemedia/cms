#!/usr/bin/env python
# coding: utf-8

import sys
sys.path.append("src")

from setuptools import setup, find_packages

setup(
    name="onespacemedia-cms",
    version="2.4.2",  # Roughly..
    url="https://github.com/onespacemedia/cms",
    author="Daniel Samuels",
    author_email="daniel@onespacemedia.com",
    license="BSD",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    description='CMS used by Onespacemedia',
    install_requires=[
        'django>=1.4,<1.5'
    ],
    package_dir = {
        "": "src",
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django :: 1.4',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
    ],
)
