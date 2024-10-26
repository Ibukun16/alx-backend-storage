#!/usr/bin/env python
"""A module that uses the Redis NoSQL datastorage/database"""
import redis
from uuid import uuid4
from functools import wraps
from typing import Any, Callable, Union, Optional


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


def replay(fn: Callable) -> None:
    """function that displays the calls history of a Cache class method"""
    r = redis.Redis()
    f_name = fn.__qualname__
    val = r.get(f_name)
    try:
        val = int(val.decode("utf-8"))
    except Exception:
        val = 0

    # print(f"{function_name} was called {value} times")
    print("{} was called {} times:".format(f_name, val))
    # inputs = r.lrange(f"{function_name}:inputs", 0, -1)
    inns = r.lrange("{}:inputs".format(f_name), 0, -1)

    # outputs = r.lrange(f"{function_name}:outputs", 0, -1)
    outs = r.lrange("{}:outputs".format(f_name), 0, -1)

    for inputt, output in zip(inns, outs):
        try:
            inputt = inputt.decode("utf-8")
        except Exception:
            inputt = ""

        try:
            output = output.decode("utf-8")
        except Exception:
            output = ""

        # print(f"{function_name}(*{input}) -> {output}")
        print("{}(*{}) -> {}".format(f_name, inputt, output))


class Cache():
    """Rep an object for storing data in a Redis database storage"""

    def __init__(self) -> None:
        """Initializing the cache instance for the function"""
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @count_calls
    @call_history
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """
        Store value in a Redis database and
        return the key to the stored value
        """
        data_key = str(uuid4())
        self._redis.set(data_key, data)
        return data_key

    def get(self, key: str, fn: Optional[callable] = None,
            ) -> Union[str, bytes, int, float]:
        """Retrieves value from a Redis database storage"""
        val = self._redis.get(key)
        return fn(val) if fn is not None else val

    def get_str(self, key: str) -> str:
        """Retrieves a string value from a Redis database storage"""
        return self.get(key, lambda x: x.decode('utf-8'))

    def get_int(self, key: str) -> int:
        """Retrieves an integer value from from a Redis database storage"""
        result = self._redis.get(key)
        try:
            result = int(result.decode("utf-8"))
        except Exception:
            result = 0
        return result
