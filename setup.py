#!/usr/bin/env python
#coding: utf-8
import os

from distutils.core import setup



def fullsplit(path, result=None):
    """
    Split a pathname into components (the opposite of os.path.join) in a
    platform-neutral way.
    """
    if result is None:
        result = []
    head, tail = os.path.split(path)
    if head == '':
        return [tail] + result
    if head == path:
        return result
    return fullsplit(head, [tail] + result)


# Compile the list of packages available, because distutils doesn't have
# an easy way to do this.
packages, data_files = [], []
root_dir = os.path.dirname(__file__)
if root_dir != '':
    os.chdir(root_dir)
cms_dir = 'cms'

for dirpath, dirnames, filenames in os.walk(cms_dir):
    # Ignore dirnames that start with '.'
    for i, dirname in enumerate(dirnames):
        if dirname.startswith('.'): del dirnames[i]
    if '__init__.py' in filenames:
        if len(fullsplit(dirpath)[1:]) > 0:
            packages.append('cms.' + '.'.join(fullsplit(dirpath)[1:]))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])





setup(
	name = "cms",
	author = "Daniel Samuels",
	author_email = "daniel@onespacemedia.com",
	version = "1.0.3",
	license = "BSD",
	url = "https://github.com/onespacemedia/cms",
	download_url = "https://github.com/onespacemedia/cms",
	description = "Onespacemedia's CMS for Django, forked from Etianen's CMS",
	py_modules = ['cms'],
	packages = packages,
    data_files = data_files,
	install_requires = ['psycopg2', 'django-suit', 'django-optimizations', 'Pillow', 'django-reversion', 'django-usertools', 'django-historylinks', 'django-watson', 'South'],
	scripts = ['cms/bin/start_cms_project.py']
)
