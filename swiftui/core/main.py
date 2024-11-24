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