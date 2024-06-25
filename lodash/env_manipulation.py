import os
from contextlib import contextmanager

@contextmanager
def set_env(**environ):
    """
    Temporarily set environment variables inside the context.
    """
    old_env = os.environ.copy()
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_env)
