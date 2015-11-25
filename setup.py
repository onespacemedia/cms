#!/usr/bin/env python
# coding: utf-8
from cms import VERSION

import platform
from setuptools import setup, find_packages


DEPENDENCIES = [
    'django',
    'Pillow',
    'sorl-thumbnail',
    'requests',
]

if platform.python_implementation() == "PyPy":
    DEPENDENCIES.append("psycopg2cffi")
else:
    DEPENDENCIES.append("psycopg2")


setup(
    name="onespacemedia-cms",
    version=".".join(str(n) for n in VERSION),
    url="https://github.com/onespacemedia/cms",
    author="Daniel Samuels",
    author_email="daniel@onespacemedia.com",
    license="BSD",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    description='CMS used by Onespacemedia',
    install_requires=DEPENDENCIES,
    extras_require={
        'usertools':  ["django-usertools"],
        'testing':  ["mock", "coverage", "coveralls", "codecov", "cookiecutter"],
        'geoip': ['geoip']
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django :: 1.7',
        'Framework :: Django :: 1.8',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
    ],
)
