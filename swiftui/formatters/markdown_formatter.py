# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

class MarkdownFormatter:
    def __init__(self, config):
        self.config = config
        self.output_dir = config.output_dir
        self.data_dir = config.data_dir