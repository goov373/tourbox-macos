"""TourBox macOS Driver

A custom macOS driver for TourBox Lite with JSON-based profiles.
"""

__version__ = "0.1.0"

from .driver import TourBoxDriver

__all__ = ["TourBoxDriver", "__version__"]
