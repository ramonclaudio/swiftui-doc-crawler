# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

import yaml
import os

class Config:
    def __init__(self, config_path=None):
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'default_config.yaml')
        
        with open(config_path, 'r') as file:
            self.config = yaml.safe_load(file)
        
        self.base_url = self.config['base_url']
        self.docs_endpoint = self.config['docs_endpoint']
        
        self.endpoint_file = self._ensure_absolute_path(self.config['endpoint_file'])
        self.processed_endpoint_file = self._ensure_absolute_path(self.config['processed_endpoint_file'])
        self.data_dir = os.path.dirname(self.endpoint_file)
        
        self.output_dir = self._ensure_absolute_path(self.config['output_dir'])
        
        self.include_links = self.config.get('include_links', False)
        
        self.sections = self.config.get('sections', {})
        self._set_section_defaults()
        
        self.use_proxy = self.config.get('use_proxy', False)
        self.request_delay = self.config['request_delay']
        self.timeout = self.config['timeout']
        self.max_retries = self.config['max_retries']
        
        self.ignored_endpoints = set(self.config.get('ignored_endpoints', []))
        
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.data_dir, exist_ok=True)