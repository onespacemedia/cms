#!/usr/bin/env python
# coding: utf-8
import platform

from setuptools import find_packages, setup

from cms import VERSION

DEPENDENCIES = [
    'python-magic',
    'requests',
    'Pillow',
    'sorl-thumbnail',
    'Jinja2>=2.10',

    'beautifulsoup4',
    'django>=2.2,<=3.2',
    'django-watson',
    'django-reversion',
    'django-jinja>=2.7.0',
]

if platform.python_implementation() == 'PyPy':
    DEPENDENCIES.append('psycopg2cffi')
else:
    DEPENDENCIES.append('psycopg2')


setup(
    name='onespacemedia-cms',
    version='.'.join(str(n) for n in VERSION),
    url='https://github.com/onespacemedia/cms',
    author='Onespacemedia',
    author_email='developers@onespacemedia.com',
    license='BSD',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    description='CMS used by Onespacemedia',
    install_requires=DEPENDENCIES,
    extras_require={
        'usertools': ['django-usertools'],
        'testing': [
            'pytest>=3.6',
            'pytest-cov',
            'pytest-django',
            'pytest-xdist',
            # / Project template
            'coveralls',
            'geoip2',
        ],
        'geoip': ['geoip2']
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Framework :: Django :: 2.2',
        'Framework :: Django :: 3.1',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
    ],
)
