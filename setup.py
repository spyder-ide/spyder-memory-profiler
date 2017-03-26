# -*- coding: utf-8 -*-
#
# Copyright © 2013 Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

from setuptools import setup, find_packages
import os
import os.path as osp


def get_version():
    """Get version from source file"""
    import codecs
    with codecs.open("spyder_memory_profiler/__init__.py", encoding="utf-8") as f:
        lines = f.read().splitlines()
        for l in lines:
            if "__version__" in l:
                version = l.split("=")[1].strip()
                version = version.replace("'", '').replace('"', '')
                return version


def get_package_data(name, extlist):
    """Return data files for package *name* with extensions in *extlist*"""
    flist = []
    # Workaround to replace os.path.relpath (not available until Python 2.6):
    offset = len(name) + len(os.pathsep)
    for dirpath, _dirnames, filenames in os.walk(name):
        for fname in filenames:
            if not fname.startswith('.') and osp.splitext(fname)[1] in extlist:
                flist.append(osp.join(dirpath, fname)[offset:])
    return flist


# Requirements
REQUIREMENTS = ['memory_profiler', 'spyder>=3']
EXTLIST = ['.jpg', '.png', '.json', '.mo', '.ini']
LIBNAME = 'spyder_memory_profiler'

LONG_DESCRIPTION = """
This is a plugin for the Spyder IDE that integrates the Python memory profiler.
It allows you to see the memory usage in every line.

Usage
-----

Add a ``@profile`` decorator to the functions that you wish to profile then
press Ctrl+Shift+F10 to run the profiler on the current script, or go to
``Run > Profile memory line by line``.

The results will be shown in a dockwidget, grouped by function. Lines with a
stronger color have the largest increments in memory usage.
"""

setup(
    name=LIBNAME,
    version=get_version(),
    packages=find_packages(),
    package_data={LIBNAME: get_package_data(LIBNAME, EXTLIST)},
    keywords=["Qt PyQt4 PyQt5 PySide spyder plugins spyplugins profiler"],
    install_requires=REQUIREMENTS,
    url='https://github.com/spyder-ide/spyder-memory-profiler',
    license='MIT',
    author='Spyder Project Contributors',
    description='Plugin for the Spyder IDE that integrates the Python'
        ' memory profiler',
    long_description=LONG_DESCRIPTION,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development',
        'Topic :: Text Editors :: Integrated Development Environments (IDE)'])
