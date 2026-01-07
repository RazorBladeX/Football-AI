import time
from functools import wraps
from typing import Any, Callable, Dict, Tuple


def ttl_cache(ttl_seconds: int = 60):
    """Simple TTL cache decorator suitable for small lookups."""

    def decorator(func: Callable):
        cache: Dict[Tuple[Any, ...], Tuple[float, Any]] = {}

        @wraps(func)
        def wrapper(*args, **kwargs):
            key = (args, tuple(sorted(kwargs.items())))
            now = time.time()
            if key in cache:
                expires_at, value = cache[key]
                if now < expires_at:
                    return value
            result = func(*args, **kwargs)
            cache[key] = (now + ttl_seconds, result)
            return result

        return wrapper

    return decorator
