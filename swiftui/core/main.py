# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

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