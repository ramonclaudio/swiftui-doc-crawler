# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

import os
import time
import requests
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
        
    def make_request(self, method, path):
        clean_path = path.lstrip('/') + '.json'
        url = f"{self.config.base_url}{self.config.docs_endpoint}{clean_path}"
        
        time.sleep(self.config.request_delay)
        
        try:
            if self.config.use_proxy:
                response = requests.request(
                    method,
                    url,
                    proxies=self.proxies,
                    auth=self.auth,
                    timeout=self.config.timeout
                )
            else:
                response = requests.request(
                    method,
                    url,
                    timeout=self.config.timeout
                )
                
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"API request failed: {str(e)}")