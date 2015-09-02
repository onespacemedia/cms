#!/usr/bin/env python
# coding: utf-8
from cms import VERSION

import platform
from setuptools import setup, find_packages
import sys


DEPENDENCIES = [
    'django',
    'django-suit',
    'Pillow',
    'django-reversion==1.8.7',
    'django-historylinks',
    'django-watson',
    'django-extensions',
    'Werkzeug',
    'opbeat',
    'bcrypt',
    'django-compressor',
    'sorl-thumbnail',
    'bcrypt',
    'onespacemedia-server-management',
    'requests',
    'python-social-auth',
    'python-memcached',
    'django-cachalot',
    'geoip',
]


if platform.python_implementation() == "PyPy":
    DEPENDENCIES.append("psycopg2cffi")
else:
    DEPENDENCIES.append("psycopg2")

if sys.version_info[0] == 3:
    DEPENDENCIES.remove("python-memcached")
    DEPENDENCIES.append("python3-memcached")
    DEPENDENCIES.remove("onespacemedia-server-management")


EXCLUDE_FROM_PACKAGES = ['cms.bin']


setup(
    name="onespacemedia-cms",
    version=".".join(str(n) for n in VERSION),
    url="https://github.com/onespacemedia/cms",
    author="Daniel Samuels",
    author_email="daniel@onespacemedia.com",
    license="BSD",
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    scripts=['cms/bin/start_cms_project.py'],
    zip_safe=False,
    entry_points={
        "console_scripts": [
            "start_cms_project.py = cms.bin.start_cms_project:main",
        ],
    },
    description='CMS used by Onespacemedia',
    install_requires=DEPENDENCIES,
    extras_require={
        'usertools':  ["django-usertools"],
        'testing':  ["mock", "coverage", "coveralls", "codecov"],
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
