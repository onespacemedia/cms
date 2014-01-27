from distutils.core import setup
import sys, os
sys.path.append("cms")

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
        print dirpath
        packages.append('.'.join(fullsplit(dirpath)[1:]))
    elif filenames:
        data_files.append([dirpath, [os.path.join(dirpath, f) for f in filenames]])
        
print packages

setup(
    name='onespacemedia-cms',
    version='1.1.1',
    description='A collection of Django extensions that add content-management facilities to Django projects.',
    author='Daniel Samuels',
    author_email='daniel@onespacemedia.com',
    url='https://github.com/onespacemedia/cms/',
    package_dir = {
        "cms": "cms",
    },
    packages = packages,
    data_files = data_files,
    scripts = ['cms/bin/start_cms_project.py'],
)
