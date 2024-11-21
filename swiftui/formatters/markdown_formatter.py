# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

class MarkdownFormatter:
    def __init__(self, config):
        self.config = config
        self.output_dir = config.output_dir
        self.data_dir = config.data_dir
    
    def _parse_link(self, title, url):
        if self.config.include_links and url:
            if url.startswith('doc://'):
                parts = url.split('/')
                try:
                    doc_index = len(parts) - 1 - parts[::-1].index('documentation')
                    clean_url = '/'.join(parts[doc_index + 1:])
                except ValueError:
                    clean_url = '/'.join(parts[2:])
                url = f"{self.config.base_url}/documentation/{clean_url}"
            return f"[{title}]({url})"
        return title

    def _get_reference_title(self, identifier, references):
        if identifier in references:
            ref = references[identifier]
            return ref.get('title', '')
        return ''