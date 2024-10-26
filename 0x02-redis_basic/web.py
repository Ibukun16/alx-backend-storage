#!/usr/bin/env python3
"""A module with tools for caching and tracking request"""
import redis
import requests
from functools import wraps
from typing import Callable


redis_store = redis.Redis()
"""Redis instance for module-level"""


def url_data_cacher(method: Callable) -> Callable:
    """Caches the output of the data fetched"""
    @wraps(method)
    def wrapper(url):
        """Function for caching the output"""
        if not redis_store.exists(f"count:{url}"):
            redis_store.set(f"count:{url}", 0)
        redis_store.incr(f"count:{url}")

        data_cache = redis_store.get(f"cached:{url}")
        if data_cache:
            return data_cache.decode("utf-8")
        html_content = func(url)
        redis_store.setex(f"cached:{url}", 10,  html_content)
        return html_content
    return wrapper


@url_data_cacher
def get_page(url: str) -> str:
    """
    Fetch and return the content of a URL after caching the request
    response and tracking the request.
    """
    return requests.get(url).text
