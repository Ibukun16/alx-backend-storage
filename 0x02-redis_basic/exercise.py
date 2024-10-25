#!/usr/bin/env python
"""A module that uses the Redis NoSQL datastorage/database"""
import redis
from uuid import uuid4
from functools import wraps
from typing import Any, Callable, Union


def count_calls(method: Callable) -> Callable:
    """
    function that tracks the number of calls
    made to a method in a cache class
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        """Call the given method after increasing its call counter"""
        if isinstance(self._redis, redis.Redis):
            self._redis.incr(method.__qualname__)
        return method(self, *args, **kwargs)
    return wrapper


def call_history(method: Callable) -> Callable:
    """
    function that tracks the call details of a
    method in a Cache class
    """
    @wraps(method)
    def wrapper(self, *args, **kwargs) -> Any:
        """
        Return the output from the method after
        storing both the input and output
        """
        inns = f"{method.__qualname__}:inputs"
        outs = f"{method.__qualname__}:outputs"
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(inns, str(args))
        result = method(self, *args, **kwargs)
        if isinstance(self._redis, redis.Redis):
            self._redis.rpush(outs, result)
        return result
    return wrapper


def replay(fn: Callable):
    """function that displays the calls history of a Cache class method"""
    if fn is None or not hasattr(fn, '__self__'):
        return
    r_store = getattr(fn.__self__, '_redis', None)
    if not isinstance(redis_store, redis.Redis):
        return
    inns = f"{fn.__qualname__}:inputs"
    outs = f"{fn.__qualname__}.outputs"
    count_calls = 0
    if r_store.exists(fn.__qualname__) != 0:
        count_calls = int(r_store.get(fn.__qualname__))
    print("{fn.__qualname__} was called {count_calls} times:")
    functn_inputs = r_store.lrange(inns, 0, -1)
    functn_outputs = r_store.lrange(outs, 0, -1)
    for f_input, f_output in zip(functn_inputs, functn_outputs):
        print(f"{fn.__qualname__}(*{f_input.decode('utf-8')}) -> {f_output}")


class Cache:
    """Rep an object for storing data in a Redis database storage"""

    def __init__(self) -> None:
        """Initializing the cache instance for the function"""
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store value in a Redis database and
        return the key to the stored value
        """
        data_key = str(uuid4())
        self._redis.set(data_key, data)
        return data_key

    def get(self, key: str, fn: Callable = None,
            ) -> Union[str, bytes, int, float]:
        """Retrieves value from a Redis database storage"""
        val = self._redis.get(key)
        return fn(val) if fn is not None else val

    def get_str(self, key: str) -> str:
        """Retrieves a string value from a Redis database storage"""
        return self.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """Retrieves an integer value from from a Redis database storage"""
        return self.get(key, lambda x: int(x))
