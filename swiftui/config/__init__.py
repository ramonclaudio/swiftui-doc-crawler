# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

from .config import Config

__all__ = ['Config']