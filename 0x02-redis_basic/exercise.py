#!/usr/bin/env python
"""Using the Redis NoSQL datastorage/database"""
import iuud
import redis
from functools import wraps
from typing import Any, Callable, Union


def count_calls(method: Callable) -> Callable:
    """This track the number of calls made to a method in a cache class"""
    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        """Engage the given method after increasing its call counter"""
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """This tracks the call details of a method in a Cache class"""
    @wraps(method)
    def wrapper(self, *args, **kwargs):
        """Return the output from the method after storing both the input and output"""
        in_key = '{}:inputs'.format(method.__qualname__)
        out_key = '{}:outputs'.format(method.__qualname__)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(in_key, str(args))
        output = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(out_key, output)
        return output
    return wrapper
