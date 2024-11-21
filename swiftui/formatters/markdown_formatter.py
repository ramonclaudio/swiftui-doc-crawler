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

    def _format_inline_content(self, inline_content, references=None):
        text_parts = []
        for inline in inline_content:
            if inline['type'] == 'text':
                text = inline['text'].strip()
                if text:
                    text_parts.append(text)
            elif inline['type'] == 'codeVoice':
                text_parts.append(f"`{inline['code']}`")
            elif inline['type'] == 'reference':
                title = None
                if references and 'identifier' in inline:
                    title = self._get_reference_title(inline['identifier'], references)
                
                if not title:
                    title = inline.get('title', '')
                if not title and 'identifier' in inline:
                    title = inline['identifier'].split('/')[-1] if 'documentation' in inline['identifier'] else ''
                
                if title:
                    if inline.get('is_active', False):
                        text_parts.append(f"`{title}`")
                    else:
                        url = inline.get('identifier', '')
                        text_parts.append(self._parse_link(title, url))
                        
        return ' '.join(part for part in text_parts if part)

    def format(self, doc_data):
        markdown = []
        sections_added = False
        
        if self.config.should_include_section('title'):
            title = doc_data['metadata']['title']
            role_heading = doc_data['metadata'].get('role_heading', '')
            if role_heading:
                markdown.append(f"# {title} ({role_heading})")
            else:
                markdown.append(f"# {title}")
        
        if self.config.should_include_section('abstract') and doc_data['abstract']:
            abstract_text = self._format_inline_content(doc_data['abstract'], doc_data['references'])
            if abstract_text:
                markdown.append(f"\n{abstract_text}")
        
        if self.config.should_include_section('availability') and doc_data['metadata']['platforms']:
            platforms = []
            for platform in doc_data['metadata']['platforms']:
                platform_str = f"{platform['name']} {platform['introduced']}+"
                if platform.get('deprecated', False):
                    platform_str += " (Deprecated)"
                platforms.append(platform_str)
            if platforms:
                markdown.append("\n## Availability")
                markdown.append("\n" + ", ".join(platforms))
                sections_added = True
        
        for section in doc_data['sections']:
            section_kind = section['kind']
            
            if not self.config.should_include_section(section_kind.replace('-', '_')):
                continue
            
            if section_kind == 'details':
                details = section.get('details', {})
                if details:
                    markdown.append("\n## Details")
                    if 'value' in details:
                        value_str = ' '.join(str(v.get('baseType', '')) for v in details['value'])
                        if value_str:
                            markdown.append(f"\n**Type**: {value_str}")
                    sections_added = True

            elif section_kind == 'parameters':
                if not any(p.get('name') for p in section['parameters']):
                    continue
                markdown.append("\n## Parameters")
                sections_added = True
                for param in section['parameters']:
                    param_name = param.get('name', '')
                    if not param_name:
                        continue
                    param_content = []
                    for content in param['content']:
                        text = self._format_inline_content(content, doc_data['references'])
                        if text:
                            param_content.append(text)
                    if param_content:
                        markdown.append(f"\n### {param_name}")
                        markdown.append(' '.join(param_content))

            elif section_kind == 'content':
                current_heading = None
                for content in section['content']:
                    if content['type'] == 'heading':
                        current_heading = content.get('text', '')
                        if current_heading.lower() == 'return value' and not self.config.should_include_section('return_value'):
                            continue
                        level = content.get('level', 2)
                        markdown.append(f"\n{'#' * level} {current_heading}")
                        sections_added = True
                    elif content['type'] == 'paragraph':
                        text = self._format_inline_content(content['content'], doc_data['references'])
                        if text:
                            markdown.append(f"\n{text}")
                    elif content['type'] == 'codeListing':
                        markdown.append("\n```swift")
                        markdown.append('\n'.join(content['code']))
                        markdown.append("```")
                    elif content['type'] == 'aside' and self.config.should_include_section('notes'):
                        style = content.get('style', '')
                        name = content.get('name', '')
                        if name or style:
                            markdown.append(f"\n> **{name or style.title()}**")
                        for aside_content in content.get('content', []):
                            text = self._format_inline_content(aside_content['content'], doc_data['references'])
                            if text:
                                markdown.append(f"> {text}")

            elif section_kind == 'declarations':
                if not sections_added:
                    markdown.append("\n## Declaration")
                else:
                    markdown.append("\n## Additional Declarations")
                sections_added = True
                
                for declaration in section['declarations']:
                    markdown.append("\n```swift")
                    markdown.append(''.join(token['text'] for token in declaration['tokens']))
                    markdown.append("```")
                    
                    if 'other_declarations' in declaration:
                        for other_decl in declaration['other_declarations']:
                            markdown.append("\n```swift")
                            markdown.append(''.join(token['text'] for token in other_decl['tokens']))
                            markdown.append("```")
        
        if self.config.should_include_section('required'):
            if doc_data['metadata'].get('required', False):
                markdown.append("\n**Required**")
        
        if self.config.should_include_section('relationships') and doc_data['relationships']:
            for relationship in doc_data['relationships']:
                if relationship['type'] == 'conformsTo' and relationship.get('identifiers'):
                    markdown.append("\n## Conforms To")
                    for identifier in relationship['identifiers']:
                        if identifier in doc_data['references']:
                            ref = doc_data['references'][identifier]
                            title = ref.get('title', '')
                            url = ref.get('url', '')
                            if title:
                                markdown.append(f"\n- {self._parse_link(title, url)}")
        
        return '\n'.join(markdown)