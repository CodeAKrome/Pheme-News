import logging
import os
from .colorize import Colorize

color = Colorize()
# Create a custom logger
logger = logging.getLogger(__name__)

# Set logging level
level = os.getenv("LOG_LEVEL")
if level:
    if level == "DEBUG":
        logger.setLevel(logging.DEBUG)
    elif level == "INFO":
        logger.setLevel(logging.INFO)
    elif level == "WARNING":
        logger.setLevel(logging.WARNING)
    elif level == "ERROR":
        logger.setLevel(logging.ERROR)
else:
    logger.setLevel(logging.ERROR)

# Set the base formatter
base_formatter = logging.Formatter(
    color.info("%(asctime)s - %(levelname)s - %(message)s")
)

# Create console handlers with different formats for each level
console_handler_info = logging.StreamHandler()
console_handler_info.setLevel(logging.INFO)
console_handler_info.setFormatter(base_formatter)

console_handler_debug = logging.StreamHandler()
console_handler_debug.setLevel(logging.DEBUG)
# Customize the debug format with additional details
debug_formatter = logging.Formatter(
    color.underline("%(asctime)s - DEBUG - %(name)s - %(lineno)d - %(message)s")
)
console_handler_debug.setFormatter(debug_formatter)

console_handler_warning = logging.StreamHandler()
console_handler_warning.setLevel(logging.WARNING)
# Customize the debug format with additional details
warning_formatter = logging.Formatter(
    color.warning("%(asctime)s - WARNING - %(name)s - %(lineno)d - %(message)s")
)
console_handler_warning.setFormatter(warning_formatter)

console_handler_error = logging.StreamHandler()
console_handler_error.setLevel(logging.ERROR)
# Customize the error format to highlight errors more clearly
error_formatter = logging.Formatter(
    color.error("%(asctime)s - ERROR - %(name)s - %(lineno)d - %(message)s")
)
console_handler_error.setFormatter(error_formatter)

# Add handlers to the logger
logger.addHandler(console_handler_info)
logger.addHandler(console_handler_debug)
logger.addHandler(console_handler_warning)
logger.addHandler(console_handler_error)

# Log messages at different levels
# logger.info('This is an info message.')
# logger.debug('This is a debug message.')
logger.warning("This is a warning message.")
# logger.error('This is an error message.')
