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