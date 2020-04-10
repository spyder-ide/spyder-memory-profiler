# Spyder memory profiler plugin

## Project details

![license](https://img.shields.io/pypi/l/spyder-memory-profiler.svg)
[![conda version](https://img.shields.io/conda/v/spyder-ide/spyder-memory-profiler.svg)](https://www.anaconda.com/download/)
[![download count](https://img.shields.io/conda/d/spyder-ide/spyder-memory-profiler.svg)](https://www.anaconda.com/download/)
[![pypi version](https://img.shields.io/pypi/v/spyder-memory-profiler.svg)](https://pypi.python.org/pypi/spyder-memory-profiler)
[![Join the chat at https://gitter.im/spyder-ide/public](https://badges.gitter.im/spyder-ide/spyder.svg)](https://gitter.im/spyder-ide/public)
[![OpenCollective Backers](https://opencollective.com/spyder/backers/badge.svg?color=blue)](#backers)
[![OpenCollective Sponsors](https://opencollective.com/spyder/sponsors/badge.svg?color=blue)](#sponsors)

## Build status

[![Windows status](https://github.com/spyder-ide/spyder-memory-profiler/workflows/Windows%20tests/badge.svg)](https://github.com/spyder-ide/spyder-memory-profiler/actions?query=workflow%3A%22Windows+tests%22)
[![Linux status](https://github.com/spyder-ide/spyder-memory-profiler/workflows/Linux%20tests/badge.svg)](https://github.com/spyder-ide/spyder-memory-profiler/actions?query=workflow%3A%22Linux+tests%22)
[![MacOS status](https://github.com/spyder-ide/spyder-memory-profiler/workflows/Macos%20tests/badge.svg)](https://github.com/spyder-ide/spyder-memory-profiler/actions?query=workflow%3A%22Macos+tests%22)

## Description

This is a plugin to run the Python
[memory_profiler](https://pypi.python.org/pypi/memory_profiler)
from within the Python IDE [Spyder](https://github.com/spyder-ide/spyder).

The code is an adaptation of the profiler plugin integrated in Spyder.

## Installation

To install this plugin, you can use either ``pip`` or ``conda`` package
managers, as follows:

Using conda (the recommended way!):

```
conda install spyder-memory-profiler -c spyder-ide
```

Using pip:

```
pip install spyder-memory-profiler
```

## Usage

Add a `@profile` decorator to the functions that you wish to profile then
Ctrl+Shift+F10 to run the profiler on the current script, or go to 
`Run > Profile memory line by line`.

The results will be shown in a dockwidget, grouped by function. Lines with a
stronger color have the largest increments in memory usage (memory profiler).

## Contributing

Everyone is welcome to contribute!

## Sponsors

Spyder and its subprojects are funded thanks to the generous support of

[![Quansight](https://static.wixstatic.com/media/095d2c_2508c560e87d436ea00357abc404cf1d~mv2.png/v1/crop/x_0,y_9,w_915,h_329/fill/w_380,h_128,al_c,usm_0.66_1.00_0.01/095d2c_2508c560e87d436ea00357abc404cf1d~mv2.png)](https://www.quansight.com/)[![Numfocus](https://i2.wp.com/numfocus.org/wp-content/uploads/2017/07/NumFocus_LRG.png?fit=320%2C148&ssl=1)](https://numfocus.org/)

and the donations we have received from our users around the world through [Open Collective](https://opencollective.com/spyder/):

[![Sponsors](https://opencollective.com/spyder/sponsors.svg)](https://opencollective.com/spyder#support)
