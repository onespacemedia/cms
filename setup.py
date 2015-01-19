#!/usr/bin/env python
#coding: utf-8
from cms import VERSION

from setuptools import setup, find_packages


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
    install_requires=[
        'django',
        'psycopg2',
        'django-suit',
        'Pillow',
        'django-reversion',
        'django-usertools',
        'django-historylinks',
        'django-watson',
        'django-extensions',
        'Werkzeug',
        'raven',
        'bcrypt'
        'django-compressor',
        'sorl-thumbnail',
        'bcrypt'
    ],
)
