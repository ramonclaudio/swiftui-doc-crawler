# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

from .main import Main

class Run:
    def __init__(self):
        self.crawler = Main()