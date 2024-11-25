# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

from .core.run import crawl

__version__ = '1.0.0'
__all__ = ['crawl']