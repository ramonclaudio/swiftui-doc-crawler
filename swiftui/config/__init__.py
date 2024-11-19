# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

from .base import Config

__all__ = ['Config']