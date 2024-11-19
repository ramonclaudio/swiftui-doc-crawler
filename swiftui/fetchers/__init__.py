# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

from .documentation import DocumentationFetcher

__all__ = ['DocumentationFetcher']