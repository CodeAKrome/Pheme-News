from functools import wraps
import traceback
from . import log

def arrest(exceptions, message=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except tuple(exceptions) as e:
                print(f"Error: {e}")
                print("Traceback:")
                traceback.print_exc()
                if message:
                    log.logger.error(message)
        return wrapper
    return decorator
