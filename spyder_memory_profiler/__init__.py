# -*- coding: utf-8 -*-
#
# Copyright © 2013 Spyder Project Contributors
# Licensed under the terms of the MIT License
# (see LICENSE.txt for details)

__version__ = '0.2.1'

# =============================================================================
# The following statements are required to register this 3rd party plugin:
# =============================================================================
from .memoryprofiler import MemoryProfiler

PLUGIN_CLASS = MemoryProfiler
