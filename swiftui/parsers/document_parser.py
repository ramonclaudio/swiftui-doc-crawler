# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

class DocumentParser:
    def __init__(self):
        self.parsed_data = None

    def parse(self, doc_data):
        try:
            self.parsed_data = {
                'metadata': self._parse_metadata(doc_data.get('metadata', {})),
                'abstract': self._parse_abstract(doc_data.get('abstract', [])),
                'sections': self._parse_sections(doc_data.get('primaryContentSections', [])),
                'relationships': self._parse_relationships(doc_data.get('relationshipsSections', [])),
                'references': self._parse_references(doc_data.get('references', {}))
            }
            return self.parsed_data
        except Exception as e:
            raise Exception(f"Documentation parsing failed: {str(e)}")