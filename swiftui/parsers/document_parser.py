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

    def _parse_abstract(self, abstract):
        if not abstract:
            return []
        
        parsed_abstract = []
        for item in abstract:
            parsed_item = {
                'type': item.get('type', ''),
                'text': item.get('text', ''),
                'code': item.get('code', '')
            }
            
            if 'inlineContent' in item:
                parsed_item['content'] = self._parse_inline_content(item['inlineContent'])
                
            parsed_abstract.append(parsed_item)
        return parsed_abstract

    def _parse_sections(self, sections):
        parsed_sections = []
        for section in sections:
            parsed_section = {
                'kind': section.get('kind', ''),
                'content': []
            }
            
            if section['kind'] == 'parameters':
                parsed_section['parameters'] = self._parse_parameters(section.get('parameters', []))
            elif section['kind'] == 'declarations':
                parsed_section['declarations'] = self._parse_declarations(section.get('declarations', []))
            elif section['kind'] == 'content':
                parsed_section['content'] = self._parse_content(section.get('content', []))
            
            parsed_sections.append(parsed_section)
        return parsed_sections

    def _parse_parameters(self, parameters):
        parsed_params = []
        for param in parameters:
            parsed_param = {
                'name': param.get('name', ''),
                'content': self._parse_content(param.get('content', []))
            }
            parsed_params.append(parsed_param)
        return parsed_params

    def _parse_declarations(self, declarations):
        parsed_decls = []
        for decl in declarations:
            parsed_decl = {
                'tokens': decl.get('tokens', []),
                'languages': decl.get('languages', [])
            }
            
            if 'otherDeclarations' in decl:
                parsed_decl['other_declarations'] = self._parse_declarations(
                    decl['otherDeclarations'].get('declarations', [])
                )
                
            parsed_decls.append(parsed_decl)
        return parsed_decls

    def _parse_content(self, content):
        parsed_content = []
        for item in content:
            parsed_item = {
                'type': item.get('type', '')
            }
            
            if item['type'] == 'paragraph':
                parsed_item['content'] = self._parse_inline_content(item.get('inlineContent', []))
            elif item['type'] == 'codeListing':
                parsed_item['code'] = item.get('code', [])
            elif item['type'] == 'heading':
                parsed_item['text'] = item.get('text', '')
                parsed_item['level'] = item.get('level', 1)
            elif item['type'] == 'aside':
                parsed_item.update({
                    'style': item.get('style', ''),
                    'name': item.get('name', ''),
                    'content': self._parse_content(item.get('content', []))
                })
                
            parsed_content.append(parsed_item)
        return parsed_content

    def _parse_inline_content(self, inline_content):
        parsed_inline = []
        for content in inline_content:
            parsed_item = {
                'type': content.get('type', '')
            }
            
            if content['type'] == 'text':
                parsed_item['text'] = content.get('text', '')
            elif content['type'] == 'codeVoice':
                parsed_item['code'] = content.get('code', '')
            elif content['type'] == 'reference':
                parsed_item.update({
                    'identifier': content.get('identifier', ''),
                    'title': content.get('title', ''),
                    'is_active': content.get('isActive', False)
                })
                
            parsed_inline.append(parsed_item)
        return parsed_inline

    def _parse_relationships(self, relationships):
        parsed_rels = []
        for rel in relationships:
            parsed_rel = {
                'type': rel.get('type', ''),
                'title': rel.get('title', ''),
                'identifiers': rel.get('identifiers', [])
            }
            parsed_rels.append(parsed_rel)
        return parsed_rels