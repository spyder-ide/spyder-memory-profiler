__version__ = '0.0.1'

# =============================================================================
# The following statements are required to register this 3rd party plugin:
# =============================================================================
from .memoryprofiler import MemoryProfiler

PLUGIN_CLASS = MemoryProfiler
