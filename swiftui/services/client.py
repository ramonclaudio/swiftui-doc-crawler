# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

from dotenv import load_dotenv

load_dotenv()

class Client:
    def __init__(self, config):
        self.config = config