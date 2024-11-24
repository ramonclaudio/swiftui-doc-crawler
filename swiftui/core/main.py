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

    def parse_collection(self, collection_path):
        try:
            with open(self.config.endpoint_file, 'r', encoding='utf-8') as file:
                endpoint_data = json.load(file)
            
            collection = self.find_collection(endpoint_data, collection_path)
            if not collection:
                raise ValueError(f"Collection {collection_path} not found")

            self.endpoint_parser.parse(collection)
            results = []
            total_endpoints = len(self.endpoint_parser.endpoints)
            
            print(f"\nParsing collection: {collection_path}")
            print(f"Found {total_endpoints} endpoints in collection")
            
            for index, endpoint_info in enumerate(self.endpoint_parser.endpoints, 1):
                path = endpoint_info['path']
                is_deprecated = endpoint_info.get('deprecated', False)
                
                if path in self.config.ignored_endpoints:
                    results.append({
                        'path': path,
                        'status': 'skipped',
                        'reason': 'ignored endpoint'
                    })
                    print(f"[{index}/{total_endpoints}] Skipping ignored endpoint: {path}")
                    continue
                
                should_parse, reason = self.metadata_parser.should_parse(
                    path, 
                    is_deprecated=is_deprecated
                )
                
                if not should_parse:
                    results.append({
                        'path': path,
                        'status': 'skipped',
                        'reason': reason
                    })
                    print(f"[{index}/{total_endpoints}] Skipping endpoint: {path} - {reason}")
                    continue
                
                try:
                    folder_path = endpoint_info['folder_path']
                    filename = endpoint_info['filename']
                    doc_path = endpoint_info['doc_path']
                    
                    print(f"[{index}/{total_endpoints}] Parsing: {path}")
                    print(f"Folder path: {folder_path}")
                    print(f"Filename: {filename}")
                    
                    success = self.parse_doc(doc_path, filename, folder_path)
                    
                    if success:
                        self.metadata_parser.mark_parsed(path, {
                            "folder_path": folder_path,
                            "filename": filename,
                            "doc_path": doc_path
                        })
                        results.append({
                            'path': path,
                            'status': 'success'
                        })
                        print(f"Successfully parsed: {path}")
                        time.sleep(self.config.request_delay)
                    else:
                        self.metadata_parser.mark_failed(path, "Parsing failed")
                        results.append({
                            'path': path,
                            'status': 'failed',
                            'reason': 'parsing error'
                        })
                        print(f"Failed to parse: {path}")
                        
                except Exception as e:
                    error_msg = str(e)
                    self.metadata_parser.mark_failed(path, error_msg)
                    results.append({
                        'path': path,
                        'status': 'failed',
                        'reason': error_msg
                    })
                    print(f"Error Parsing {path}: {error_msg}")
                    continue

            success_count = sum(1 for r in results if r['status'] == 'success')
            failed_count = sum(1 for r in results if r['status'] == 'failed')
            skipped_count = sum(1 for r in results if r['status'] == 'skipped')
            
            print(f"\nCollection Parsing Complete:")
            print(f"Total endpoints: {total_endpoints}")
            print(f"Successfully parsed: {success_count}")
            print(f"Failed: {failed_count}")
            print(f"Skipped: {skipped_count}")
            
            return results

        except Exception as e:
            error_msg = str(e)
            print(f"Error Parsing collection: {error_msg}")
            return {'error': error_msg}

    def crawl(self, target_path=None, mode='all'):
        try:
            if mode in ['single', 'collection'] and not target_path:
                raise ValueError("target_path is required for single endpoint and collection Parsing")

            if target_path:
                target_path = self.extract_path_from_url(target_path)

            if mode == 'single':
                result = self.parse_single_endpoint(target_path)
                self.response = {'results': [result]}
                return self.response
                
            elif mode == 'collection':
                results = self.parse_collection(target_path)
                self.response = {'results': results}
                return self.response
                
            elif mode == 'all':
                with open(self.config.endpoint_file, 'r', encoding='utf-8') as file:
                    endpoint_data = json.load(file)
                
                self.endpoint_parser.parse(endpoint_data)
                total_endpoints = len(self.endpoint_parser.endpoints)
                parsed_count = 0
                
                print(f"Starting to parse {total_endpoints} endpoints...")
                
                results = []
                for endpoint_info in self.endpoint_parser.endpoints:
                    path = endpoint_info['path']
                    is_deprecated = endpoint_info.get('deprecated', False)
                    parsed_count += 1
                    
                    if path in self.config.ignored_endpoints:
                        results.append({
                            'path': path,
                            'status': 'skipped',
                            'reason': 'ignored endpoint'
                        })
                        print(f"[{parsed_count}/{total_endpoints}] Skipping ignored endpoint: {path}")
                        continue
                    
                    should_parse, reason = self.metadata_parser.should_parse(
                        path, 
                        is_deprecated=is_deprecated
                    )
                    
                    if not should_parse:
                        results.append({
                            'path': path,
                            'status': 'skipped',
                            'reason': reason
                        })
                        print(f"[{parsed_count}/{total_endpoints}] Skipping endpoint: {path} - {reason}")
                        continue
                    
                    try:
                        folder_path = endpoint_info['folder_path']
                        filename = endpoint_info['filename']
                        doc_path = endpoint_info['doc_path']
                        
                        print(f"[{parsed_count}/{total_endpoints}] Parsing: {path}")
                        print(f"Folder path: {folder_path}")
                        print(f"Filename: {filename}")
                        
                        success = self.parse_doc(doc_path, filename, folder_path)
                        
                        if success:
                            self.metadata_parser.mark_parsed(path, {
                                "folder_path": folder_path,
                                "filename": filename,
                                "doc_path": doc_path
                            })
                            results.append({
                                'path': path,
                                'status': 'success'
                            })
                            print(f"Successfully parsed: {path}")
                            time.sleep(self.config.request_delay)
                        else:
                            self.metadata_parser.mark_failed(path, "Parsing failed")
                            results.append({
                                'path': path,
                                'status': 'failed',
                                'reason': 'Parsing error'
                            })
                            print(f"Failed to parse: {path}")
                            
                    except Exception as e:
                        error_msg = str(e)
                        self.metadata_parser.mark_failed(path, error_msg)
                        results.append({
                            'path': path,
                            'status': 'failed',
                            'reason': error_msg
                        })
                        print(f"Error Parsing {path}: {error_msg}")
                        continue
                
                stats = self.metadata_parser.get_statistics()
                self.response = {
                    'results': results,
                    'statistics': stats
                }
                
                print("\nGenerating Statistics:")
                print(f"Total parsed: {stats['total_parsed']}")
                print(f"Total failed: {stats['total_failed']}")
                print(f"Total deprecated: {stats['total_deprecated']}")
                print(f"Last updated: {stats['last_updated']}")
                
                return self.response
            
            else:
                raise ValueError(f"Invalid mode: {mode}. Must be 'all', 'single', or 'collection'")
                
        except Exception as e:
            error_msg = f"An error occurred: {str(e)}"
            print(error_msg)
            self.response = {'error': error_msg}
            return self.response