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
    @wrap(method)
    def wrapper(url) -> str:
        """Function for caching the output"""
        output = redis_store.get(f"cached:{url}")
        if output:
            return output.decode('utf-8')
        html_content = method(url)
        redis_store.incr(f"count:{url}")
        redis_store.set(f"cached:{url}", html_content, ex=10)
        redis_store.expire(f"cached:{url}", 10)
        return html_content
    return wrapper


@url_data_cacher
def get_page(url: str) -> str:
    """
    Return the content of a URL after caching the request response,
    and tracking the request.
    """
    return requests.get(url).text


if __name__ == "__main__":
    get_page("http//slowly.robertomurray.co.uk")
