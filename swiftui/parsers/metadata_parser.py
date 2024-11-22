# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

import json
import os
from datetime import datetime

class MetadataParser:
    def __init__(self, filepath):
        self.filepath = filepath
        self.data = self._load_data()
    
    def _load_data(self):
        try:
            with open(self.filepath, 'r') as file:
                data = json.load(file)
                if isinstance(data.get("deprecated_endpoints", []), list):
                    deprecated_dict = {}
                    for endpoint in data["deprecated_endpoints"]:
                        deprecated_dict[endpoint] = {
                            "marked_at": datetime.now().isoformat(),
                            "reason": "Legacy deprecation"
                        }
                    data["deprecated_endpoints"] = deprecated_dict
                return data
        except (FileNotFoundError, json.JSONDecodeError):
            return {
                "metadata": {
                    "last_updated": datetime.now().isoformat(),
                    "version": "1.0"
                },
                "processed_endpoints": {},
                "failed_endpoints": {},
                "deprecated_endpoints": {}
            }
    
    def _save_data(self):
        data_to_save = self.data.copy()
        data_to_save["metadata"]["last_updated"] = datetime.now().isoformat()
        
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        
        with open(self.filepath, 'w') as file:
            json.dump(data_to_save, file, indent=2, sort_keys=True)