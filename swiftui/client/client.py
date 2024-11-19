# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

import os
import time
import requests
from dotenv import load_dotenv
from requests.auth import HTTPProxyAuth

load_dotenv()

proxy_host = os.getenv('PROXY_HOST')
proxy_port = os.getenv('PROXY_PORT')
proxy_username = os.getenv('PROXY_USERNAME')
proxy_password = os.getenv('PROXY_PASSWORD')

proxies = {
    'http': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
    'https': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
}

auth = HTTPProxyAuth(proxy_username, proxy_password)

class Client:
    def __init__(self, config):
        self.config = config
        
    def _make_request(self, method, path):
        clean_path = path.lstrip('/') + '.json'
        url = f"{self.config.base_url}{self.config.docs_endpoint}{clean_path}"
        
        time.sleep(self.config.request_delay)
        
        if self.config.use_proxy == True:
            response = requests.request(method, url, proxies=proxies, auth=auth)
        else:
            response = requests.request(method, url)
            
        response.raise_for_status()
        return response.json()