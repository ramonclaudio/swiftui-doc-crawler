# Prevent caching of bytecode
import sys
sys.dont_write_bytecode = True

import os
import json
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
    
    def should_parse(self, endpoint, is_deprecated=False):
        if is_deprecated:
            self.mark_deprecated(endpoint, "Current API deprecation")
            return False, "Deprecated endpoint"
            
        if endpoint in self.data["deprecated_endpoints"]:
            return False, f"Previously marked as deprecated: {self.data['deprecated_endpoints'][endpoint].get('reason', 'Unknown reason')}"
            
        if endpoint in self.data["processed_endpoints"]:
            return False, "Already parsed"
            
        return True, "Ready for parsing"
    
    def mark_deprecated(self, endpoint, reason="Not specified"):
        if endpoint not in self.data["deprecated_endpoints"]:
            self.data["deprecated_endpoints"][endpoint] = {
                "marked_at": datetime.now().isoformat(),
                "reason": reason
            }
            self._save_data()
    
    def mark_parsed(self, endpoint, metadata=None):
        self.data["processed_endpoints"][endpoint] = {
            "parsed_at": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        self.data["failed_endpoints"].pop(endpoint, None)
        self._save_data()
    
    def mark_failed(self, endpoint, error_message):
        current_failures = self.data["failed_endpoints"].get(endpoint, {"attempts": 0})
        current_failures["attempts"] += 1
        current_failures["last_error"] = error_message
        current_failures["last_attempt"] = datetime.now().isoformat()
        
        self.data["failed_endpoints"][endpoint] = current_failures
        self._save_data()
    
    def get_statistics(self):
        return {
            "total_parsed": len(self.data["processed_endpoints"]),
            "total_failed": len(self.data["failed_endpoints"]),
            "total_deprecated": len(self.data["deprecated_endpoints"]),
            "last_updated": self.data["metadata"]["last_updated"]
        }