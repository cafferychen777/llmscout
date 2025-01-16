import json
import os
from typing import Dict, Any

def save_json(data: Any, filepath: str) -> None:
    """Save data to JSON file"""
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def load_json(filepath: str) -> Any:
    """Load data from JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)

def ensure_directory(directory: str) -> None:
    """Ensure directory exists"""
    os.makedirs(directory, exist_ok=True)