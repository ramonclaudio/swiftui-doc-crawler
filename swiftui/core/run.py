# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

from .main import Main

class Run:
    def __init__(self):
        self.crawler = Main()

    def _run(self, operation_name, *args, **kwargs):
        operation = getattr(self.crawler, operation_name)
        response = operation(*args, **kwargs)
        return self.crawler.get_response()

    def crawl(self, target_path=None, mode='all'):
        return self._run('crawl', target_path=target_path, mode=mode)