def mute_method_unless(var):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if not var:
                return None
            return func(*args, **kwargs)
        return wrapper
    return decorator
