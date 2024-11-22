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

    def _parse_metadata(self, metadata):
        return {
            'title': metadata.get('title', ''),
            'role_heading': metadata.get('roleHeading', ''),
            'platforms': self._parse_platforms(metadata.get('platforms', [])),
            'required': metadata.get('required', False)
        }

    def _parse_platforms(self, platforms):
        parsed_platforms = []
        for platform in platforms:
            parsed_platforms.append({
                'name': platform.get('name', ''),
                'introduced': platform.get('introducedAt', ''),
                'deprecated': platform.get('deprecated', False)
            })
        return parsed_platforms