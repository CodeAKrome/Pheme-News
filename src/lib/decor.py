import functools
import traceback
import sys

"""Decorator to catch listed exceptions with optional message and logging to stderr."""


def log_error(error_message, log_file=None):
    """Log an error message to stdout or a file handle.

    Args:
        error_message (str): The error message to log.
        log_file (file): The file handle to use for logging. If None, use stderr.
    """
    if log_file is None:
        log_file = sys.stderr

    try:
        print(error_message, file=log_file)
        log_file.flush()
    except Exception as e:
        # If an error occurs while logging the error, print to stderr instead
        print(f"Failed to log error: {e}", file=sys.stderr)


def handler(e: Exception, func, msg: str = ""):
    """Exceptional dump"""
    ex_type = type(e).__name__
    ex_message = str(e)
    # Difference between call as standalone (str) and arrest() which passes function
    if isinstance(func, str):
        f = func
    else:
        f = func.__name__
    preamble = f"Function {f} raised {ex_type} error message: {ex_message}"
    if msg:
        log_error(f"Arrested: {msg} {preamble}")
    else:
        log_error(preamble)
    log_error("Traceback:")
    for frame in traceback.extract_tb(sys.exc_info()[2]):
        fname, lineno, fn, text = frame
        log_error(f"{lineno}:\t{fname}\n{fn}:\t{text})")


def arrest(catch: list = [], msg: str = "", log_file=None):
    """Catch exceptions from list and optionally add message."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except tuple(catch) as e:
                handler(e, func, msg)

        return wrapper

    return decorator


def test_self():
    """Run selftest"""

    @arrest([ValueError, TypeError], "Invalid argument")
    def my_function(x: float):
        return x * 2.3

    # test the function with invalid input
    print(my_function(["hello", "goodbye"]))


if __name__ == "__main__":
    test_self()
