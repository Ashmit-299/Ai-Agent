# video/failed_cases.py
import os
import json
import time
from pathlib import Path

FAILED_CASES_DIR = "reports/failed_storyboards"

def archive_failed_storyboard(input_data: str, error_message: str, error_type: str):
    """Archive failed storyboard cases without overwriting"""
    os.makedirs(FAILED_CASES_DIR, exist_ok=True)
    
    timestamp = int(time.time())
    filename = f"failed_{timestamp}_{hash(input_data) % 10000}.json"
    filepath = os.path.join(FAILED_CASES_DIR, filename)
    
    # Ensure no overwrite
    counter = 1
    while os.path.exists(filepath):
        base_name = f"failed_{timestamp}_{hash(input_data) % 10000}_{counter}.json"
        filepath = os.path.join(FAILED_CASES_DIR, base_name)
        counter += 1
    
    failed_case = {
        "timestamp": timestamp,
        "input_data": input_data[:500],  # Truncate for storage
        "error_message": str(error_message),
        "error_type": error_type,
        "archived_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    with open(filepath, 'w') as f:
        json.dump(failed_case, f, indent=2)
    
    return filepath