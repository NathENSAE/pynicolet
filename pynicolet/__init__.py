"""
pynicolet
=========

A lightweight Python library for reading legacy Nicolet EEG files.

Exports:
    NicoletReader: Main class for reading files.
"""

from .reader import NicoletReader

__version__ = "0.1.0"
__all__ = ["NicoletReader"]
