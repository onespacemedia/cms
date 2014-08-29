#!/usr/bin/env python
#coding: utf-8

from setuptools import setup, find_packages


EXCLUDE_FROM_PACKAGES = ['cms.bin']

setup(
    name="onespacemedia-cms",
    version="1.0.5",
    url="https://github.com/onespacemedia/cms",
    author="Daniel Samuels",
    author_email="daniel@onespacemedia.com",
    license="BSD",
    packages=find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    include_package_data=True,
    scripts=['cms/bin/start_cms_project.py'],
    zip_safe=False,
    description='CMS used by Onespacemedia',
    install_requires=['psycopg2', 'django-suit', 'django-optimizations', 'Pillow', 'django-reversion', 'django-usertools', 'django-historylinks', 'django-watson', 'South'],
)
