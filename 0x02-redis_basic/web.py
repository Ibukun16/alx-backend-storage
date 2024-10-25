#!/usr/bin/env python3
"""A module with tools for caching and tracking request"""
import redis
import requests
from functools import wraps
from typing import Callable


redis_store = redis.Redis()
"""Redis instance for module-level"""



def data_cacher(method: Callable) -> Callable:
    """Caches the output of the data fetched"""
    @wrap(method)
    def wrapper(url) -> str:
        """Wrapper function for caching output"""
        redis_store.incr(f"count:{url}")
        output = redis_store.get(f"result:{url}")
        if output:
            return output.decode('utf-8')
        output = method(url)
        redis_store.set(f"count:{url}", 0)
        redis_store.setex(f"output:{url}", 10, output)
        return output
    return wrapper


@data_cacher
def get_page(url: str) -> str:
    """
    Return the content of a URL after caching the request response,
    and tracking the request.
    """
    return requests.get(url).text
