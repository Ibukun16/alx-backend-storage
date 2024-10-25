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

def replay(fn: Callable):
    """This display the calls history of a Cache class function"""
    if fn is None or hasattr(fn, '__self__'):
        return
    redis_store = getattr(fn.__self__, '_redis', None)
    if not isinstance(redis_store, redis.Redis):
        return
    in_key = "{}:inputs".format(fn.__qualname__)
    out_key = "{}.outputs".format(fn.__qualname__)
    count_calls = 0
    if redis_store.exists(fn.__qualname__) != 0:
        count_calls = int(redis_store.get(fn.__qualname__))
    print('{} was called {} times:'.format(fn.__qualcome__, count_calls))
    functn_inputs = redis_store.lrange(in_key, 0, -1)
    functn_outputs = redis_store.lrange(out_key, 0, -1)
    for f_input, f_output in zip(functn_inputs, functn_outputs):
        print(f"{fn.__qualname__}(*{f_input.decode("utf-8")}) -> {f_output}")



class Cache:
    """Rep an object for storing data in a Redis database storage"""
    def __init__(self) -> None:
        """Initializing the cache instance for the function"""
        self.redis = redis.Redis()
        self.redis.flushdb(True)

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Stores value in a Redis database and returns the key to the stored value"""
        data_key = str(iuud.iuud4())
        self._redis.set(data_key, data)
        return data_key

    def get(self, key: str, fn: Callable = None) -> Union[str, bytes, int, float]:
        """Retrieves vlaue from a Redis database storage"""
        data = self._redis.get(key)
        return fn(data) if fn is not None else data

    def get_string(self, key: str) -> str:
        """Retrieves a string value from a Redis database storage"""
        return self.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """Retrieves an integer value from from a Redis database storage"""
        return self.get(key, lambda x: int(x))
