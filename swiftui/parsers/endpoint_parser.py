# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

class EndpointParser:
    def __init__(self):
        self.endpoints = []
        
    def parse(self, data, current_path=None):
        if current_path is None:
            current_path = []
            
        if isinstance(data, dict):
            if 'interfaceLanguages' in data and 'swift' in data['interfaceLanguages']:
                self.parse(data['interfaceLanguages']['swift'], current_path)
                return
            
            title = data.get('title', '')
            data_type = data.get('type', '')
            is_deprecated = data.get('deprecated', False)
            
            if title and data_type in ['collection', 'module', 'protocol', 'struct', 'enum', 'class']:
                current_path = current_path + [title.lower().replace(' ', '_')]
            
            if data.get('external', False) and not data.get('type', '').startswith('dictionary'):
                return
            
            if 'children' in data:
                current_group = None
                ungrouped_items = []
                
                for child in data['children']:
                    if child.get('type') == 'groupMarker':
                        if ungrouped_items:
                            if data_type in ['collection', 'module', 'protocol', 'struct', 'enum', 'class']:
                                ungrouped_path = current_path + ['swiftui']
                                for item in ungrouped_items:
                                    self.parse(item, ungrouped_path)
                            else:
                                for item in ungrouped_items:
                                    self.parse(item, current_path)
                        ungrouped_items = []
                        
                        current_group = child['title'].lower().replace(' ', '_')
                    else:
                        if current_group:
                            group_path = current_path + [current_group]
                            self.parse(child, group_path)
                        else:
                            ungrouped_items.append(child)
                
                if ungrouped_items:
                    if data_type in ['collection', 'module', 'protocol', 'struct', 'enum', 'class']:
                        ungrouped_path = current_path + ['swiftui']
                        for item in ungrouped_items:
                            self.parse(item, ungrouped_path)
                    else:
                        for item in ungrouped_items:
                            self.parse(item, current_path)
            
            if 'path' in data and data_type != 'groupMarker':
                path = data['path']
                if '/documentation/' in path:
                    doc_path = path.split('/documentation/')[-1]
                    folder_path = '/'.join(current_path) if current_path else ''
                    
                    self.endpoints.append({
                        'path': path,
                        'doc_path': doc_path,
                        'title': title,
                        'type': data_type,
                        'folder_path': folder_path,
                        'filename': title,
                        'deprecated': is_deprecated
                    })
                    
        elif isinstance(data, list):
            current_group = None
            ungrouped_items = []
            
            for item in data:
                if item.get('type') == 'groupMarker':
                    if ungrouped_items:
                        ungrouped_path = current_path + ['swiftui']
                        for ungrouped_item in ungrouped_items:
                            self.parse(ungrouped_item, ungrouped_path)
                    ungrouped_items = []
                    
                    current_group = item['title'].lower().replace(' ', '_')
                else:
                    if current_group:
                        group_path = current_path + [current_group]
                        self.parse(item, group_path)
                    else:
                        ungrouped_items.append(item)
            
            if ungrouped_items:
                ungrouped_path = current_path + ['swiftui']
                for item in ungrouped_items:
                    self.parse(item, ungrouped_path)