"""
Debug logging utility for Hebrew matcher
Writes NDJSON logs to debug.log file
"""
import json
import time
import os
from pathlib import Path

# Use the exact path from system reminder: /Users/jhonny/davar/.cursor/debug.log
# Fallback to workspace root if .cursor not accessible  
DEBUG_LOG_PATH = Path('/Users/jhonny/davar/.cursor/debug.log')
FALLBACK_LOG_PATH = Path('/Users/jhonny/davar/debug.log')

def debug_log(location: str, message: str, data: dict = None, hypothesis_id: str = None, run_id: str = 'debug-unmatched'):
    """Write a debug log entry in NDJSON format"""
    log_entry = {
        'id': f"log_{int(time.time() * 1000)}",
        'timestamp': int(time.time() * 1000),
        'location': location,
        'message': message,
        'data': data or {},
        'sessionId': 'debug-session',
        'runId': run_id,
        'hypothesisId': hypothesis_id
    }
    
    # Try .cursor/debug.log first, fallback to workspace root
    log_path = DEBUG_LOG_PATH
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(log_path, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except (PermissionError, OSError, FileNotFoundError):
        # Fallback to workspace root if .cursor not accessible
        try:
            with open(FALLBACK_LOG_PATH, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception:
            pass  # Silently fail if logging not possible
