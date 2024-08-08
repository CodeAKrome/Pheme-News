from functools import wraps
import traceback
from .log import logger as logger


def arrest(exceptions, message=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except tuple(exceptions) as e:
                print(f"Error: {e}")
                print("Traceback:")
                logger.error(traceback.format_exc())
                if message:
                    logger.error(message)

        return wrapper

    return decorator
