# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

import os
from dotenv import load_dotenv
from requests.auth import HTTPProxyAuth

load_dotenv()

class Client:
    def __init__(self, config):
        self.config = config
        self._setup_proxy()
        
    def _setup_proxy(self):
        if self.config.use_proxy:
            proxy_host = os.getenv('PROXY_HOST')
            proxy_port = os.getenv('PROXY_PORT')
            proxy_username = os.getenv('PROXY_USERNAME')
            proxy_password = os.getenv('PROXY_PASSWORD')

            if not all([proxy_host, proxy_port, proxy_username, proxy_password]):
                raise Exception("Proxy credentials are missing")

            self.proxies = {
                'http': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
                'https': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
            }
            self.auth = HTTPProxyAuth(proxy_username, proxy_password)
        else:
            self.proxies = None
            self.auth = None