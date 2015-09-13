spyder.memory_profiler
=====================

Description
-----------

This is a plugin to run the python `memory_profiler <https://pypi.python.org/pypi/memory_profiler>`_ from within the `spyder <https://code.google.com/p/spyderlib/>`_ editor.

The code is an adaptation of the profiler plugin integrated in `spyder <https://github.com/spyder-ide/spyder.memory_profiler>`_.

Install instructions
--------------------


Usage
-----

Add a ``@profile`` decorator to the functions that you wish to profile then Ctrl+Shift+F10 to run the profiler on the current script, or go to ``Run > Profile memory line by line``.

The results will be shown in a dockwidget, grouped by function. Lines with a stronger color have the largest increments in memory usage (memory profiler).

Screenshot
----------

Line profiler:

.. image:: spyder_line_profiler.png
