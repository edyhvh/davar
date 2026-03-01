"""
v2 Dictionary-based Strong's assignment system for Delitzsch Hebrew NT.

This module provides a pure dictionary-based approach to assigning Strong's numbers
to Hebrew words with null values, without using any API calls.
"""

__version__ = "2.0.0"

from .processor import StrongsProcessorV2
from .dictionary_index import DictionaryIndex
from .matcher import StrongMatcher

__all__ = ['StrongsProcessorV2', 'DictionaryIndex', 'StrongMatcher']