spyder-memory-profiler
======================

Project information 
-------------------

.. image:: https://img.shields.io/pypi/l/spyder-memory-profiler.svg
   :target: https://github.com/spyder-ide/spyder-memory-profiler/blob/master/LICENSE.txt
   
.. image:: https://img.shields.io/pypi/v/spyder-memory-profiler.svg
   :target: https://pypi.python.org/pypi/spyder-memory-profiler

.. image:: https://badges.gitter.im/spyder-ide/spyder.svg
   :target: https://gitter.im/spyder-ide/public

.. image:: https://opencollective.com/spyder/backers/badge.svg?color=blue
   :target: #backers
   :alt: OpenCollective Backers

.. image:: https://opencollective.com/spyder/sponsors/badge.svg?color=blue
   :target: #sponsors
   :alt: OpenCollective Sponsors

Build information
-----------------

.. image:: https://travis-ci.org/spyder-ide/spyder-memory-profiler.svg?branch=master
   :target: https://travis-ci.org/spyder-ide/spyder-memory-profiler

.. image:: https://ci.appveyor.com/api/projects/status/gd88722qallyheoe/branch/master?svg=true
   :target: https://ci.appveyor.com/project/spyder-ide/spyder-memory-profiler

.. image:: https://circleci.com/gh/spyder-ide/spyder-memory-profiler/tree/master.svg?style=shield
   :target: https://circleci.com/gh/spyder-ide/spyder-memory-profiler/tree/master

.. image:: https://coveralls.io/repos/github/spyder-ide/spyder-memory-profiler/badge.svg?branch=master
   :target: https://coveralls.io/github/spyder-ide/spyder-memory-profiler?branch=master

.. image:: https://www.quantifiedcode.com/api/v1/project/4a08fcbf42db40589ec02efd38597e8a/badge.svg
  :target: https://www.quantifiedcode.com/app/project/4a08fcbf42db40589ec02efd38597e8a

.. image:: https://scrutinizer-ci.com/g/spyder-ide/spyder-memory-profiler/badges/quality-score.png?b=master
   :target: https://scrutinizer-ci.com/g/spyder-ide/spyder-memory-profiler/?branch=master)

Important Announcement: Spyder is unfunded!
-------------------------------------------

Since mid November/2017, [Anaconda, Inc](https://www.anaconda.com/) has
stopped funding Spyder development, after doing it for the past 18
months. Because of that, development will focus from now on maintaining
Spyder 3 at a much slower pace than before.

If you want to contribute to maintain Spyder, please consider donating at

https://opencollective.com/spyder

We appreciate all the help you can provide us and can't thank you enough for
supporting the work of Spyder devs and Spyder development.

If you want to know more about this, please read this
[page](https://github.com/spyder-ide/spyder/wiki/Anaconda-stopped-funding-Spyder).

Description
-----------

This is a plugin to run the python `memory_profiler <https://pypi.python.org/pypi/memory_profiler>`_ from within the python IDE `spyder <https://github.com/spyder-ide/spyder>`_.

The code is an adaptation of the profiler plugin integrated in `spyder <https://github.com/spyder-ide/spyder>`_.

Install instructions
--------------------

The memory-profiler plugin is available in the ``spyder-ide`` channel in
Anaconda and in PyPI, so it can be installed with the following
commands:

* Using Anaconda: ``conda install -c spyder-ide spyder-memory-profiler``
* Using pip: ``pip install spyder-memory-profiler``

All dependencies will be automatically installed. You have to restart
Spyder before you can use the plugin.


Usage
-----

Add a ``@profile`` decorator to the functions that you wish to profile then Ctrl+Shift+F10 to run the profiler on the current script, or go to ``Run > Profile memory line by line``.

The results will be shown in a dockwidget, grouped by function. Lines with a stronger color have the largest increments in memory usage (memory profiler).

Contributing
------------

Everyone is welcome to contribute!

Backers
~~~~~~~

Support us with a monthly donation and help us continue our activities.

.. image:: https://opencollective.com/spyder/backers.svg
   :target: https://opencollective.com/spyder#support
   :alt: Backers

Sponsors
~~~~~~~~

Become a sponsor to get your logo on our README on Github.

.. image:: https://opencollective.com/spyder/sponsors.svg
   :target: https://opencollective.com/spyder#support
   :alt: Sponsors
