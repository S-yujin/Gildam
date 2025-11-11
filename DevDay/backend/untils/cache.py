import time
from functools import wraps

def cache(ttl: int = 300):
    def decorator(fn):
        store = {}
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()
            if key in store:
                ts, val = store[key]
                if now - ts < ttl:
                    return val
            val = fn(*args, **kwargs)
            store[key] = (now, val)
            return val
        return wrapper
    return decorator
