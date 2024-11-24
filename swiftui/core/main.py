# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

import json
import time
from pathlib import Path

from ..config.config import Config
from ..services.client import Client
from ..parsers.document_parser import DocumentParser
from ..parsers.endpoint_parser import EndpointParser
from ..parsers.metadata_parser import MetadataParser
from ..formatters.markdown_formatter import MarkdownFormatter

class Main:
    def __init__(self, config_path="swiftui/config/default_config.yaml"):
        self.config = Config(config_path)
        self.client = Client(self.config)
        self.formatter = MarkdownFormatter(self.config)
        self.endpoint_parser = EndpointParser()
        self.document_parser = DocumentParser()
        self.metadata_parser = MetadataParser(self.config.processed_endpoint_file)
        self.response = None
        
        Path(self.config.output_dir).mkdir(parents=True, exist_ok=True)
        Path(self.config.data_dir).mkdir(parents=True, exist_ok=True)

    def extract_path_from_url(self, url_or_path):
        if not url_or_path:
            return None
            
        if url_or_path.startswith(('/documentation/', '/tutorials/')):
            return url_or_path
            
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url_or_path)
            path = parsed.path
            
            if parsed.netloc != 'developer.apple.com':
                raise ValueError("URL must be from developer.apple.com domain")
                
            if '/documentation/' in path or '/tutorials/' in path:
                path_parts = path.split('/documentation/')
                if len(path_parts) > 1:
                    return f"/documentation/{path_parts[1]}"
                path_parts = path.split('/tutorials/')
                if len(path_parts) > 1:
                    return f"/tutorials/{path_parts[1]}"
                    
            raise ValueError("URL must contain /documentation/ or /tutorials/ path")
            
        except Exception as e:
            raise ValueError(f"Invalid documentation URL or path: {str(e)}")
    
    def parse_doc(self, endpoint, filename, folder_path=''):
        try:
            doc_data = self.client.make_request(method="GET", path=endpoint)
            parsed_data = self.document_parser.parse(doc_data)
            markdown = self.formatter.format(parsed_data)
            self.formatter.save_markdown(filename, markdown, folder_path)
            return True
        except Exception as e:
            print(f"Error parsing {endpoint}: {str(e)}")
            return False

    def get_response(self):
        return self.response

    def parse_single_endpoint(self, path):
        try:
            with open(self.config.endpoint_file, 'r', encoding='utf-8') as file:
                endpoint_data = json.load(file)
            
            found_endpoint = None
            self.endpoint_parser.parse(endpoint_data)
            for endpoint in self.endpoint_parser.endpoints:
                if endpoint['path'] == path:
                    found_endpoint = endpoint
                    break
            
            if not found_endpoint:
                raise ValueError(f"Endpoint {path} not found in documentation")

            should_parse, reason = self.metadata_parser.should_parse(
                path, 
                is_deprecated=found_endpoint.get('deprecated', False)
            )

            if not should_parse:
                return {'status': 'skipped', 'path': path, 'reason': reason}

            success = self.parse_doc(
                found_endpoint['doc_path'],
                found_endpoint['filename'],
                found_endpoint['folder_path']
            )

            if success:
                self.metadata_parser.mark_parsed(path, {
                    "folder_path": found_endpoint['folder_path'],
                    "filename": found_endpoint['filename'],
                    "doc_path": found_endpoint['doc_path']
                })
                return {'status': 'success', 'path': path}
            else:
                self.metadata_parser.mark_failed(path, "Parsing failed")
                return {'status': 'failed', 'path': path, 'reason': 'parsing error'}

        except Exception as e:
            error_msg = str(e)
            self.metadata_parser.mark_failed(path, error_msg)
            return {'status': 'failed', 'path': path, 'reason': error_msg}

    def find_collection(self, data, target_path):
        if isinstance(data, dict):
            if 'interfaceLanguages' in data and 'swift' in data['interfaceLanguages']:
                return self.find_collection(data['interfaceLanguages']['swift'], target_path)
            
            if data.get('path') == target_path:
                return data
                
            for key, value in data.items():
                if isinstance(value, (dict, list)):
                    result = self.find_collection(value, target_path)
                    if result:
                        return result
                        
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, (dict, list)):
                    result = self.find_collection(item, target_path)
                    if result:
                        return result
        return None