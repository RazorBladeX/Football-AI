import time
from collections import OrderedDict
from functools import wraps
from typing import Any, Callable, Dict, Tuple


def ttl_cache(ttl_seconds: int = 60):
    """Simple TTL cache decorator suitable for small lookups."""

    def decorator(func: Callable):
        cache: "OrderedDict[Tuple[Any, ...], Tuple[float, Any]]" = OrderedDict()

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()
            if key in cache:
                expires_at, value = cache.pop(key)
                cache[key] = (expires_at, value)
                if now < expires_at:
                    return value
            result = func(*args, **kwargs)
            cache[key] = (now + ttl_seconds, result)
            if len(cache) > 256:
                cache.popitem(last=False)
            return result

        return wrapper

    return decorator
