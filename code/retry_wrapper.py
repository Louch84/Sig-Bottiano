#!/usr/bin/env python3
"""
Auto-retry with error logging
"""

import time
import functools
import os
from datetime import datetime

ERROR_LOG = os.path.expanduser("~/.openclaw/workspace/logs/errors.log")

def log_error(func_name, error):
    """Log error for pattern analysis"""
    os.makedirs(os.path.dirname(ERROR_LOG), exist_ok=True)
    timestamp = datetime.now().isoformat()
    with open(ERROR_LOG, 'a') as f:
        f.write(f"{timestamp} | {func_name} | {error}\n")

def retry(max_attempts=3, delay=1, backoff=2):
    """Retry decorator with exponential backoff"""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 1
            while attempt <= max_attempts:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts:
                        log_error(func.__name__, str(e))
                        raise
                    wait_time = delay * (backoff ** (attempt - 1))
                    time.sleep(wait_time)
                    attempt += 1
        return wrapper
    return decorator

# Usage: @retry(max_attempts=3)
# def my_function():
#     pass
