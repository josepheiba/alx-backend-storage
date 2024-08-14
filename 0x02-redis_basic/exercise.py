#!/usr/bin/env python3
""""A module for using the Redis NoSQL data storage"""

import redis
import uuid
from typing import Callable, Union
import functools


def count_calls(method: Callable) -> Callable:
    """Decorator to count the number of times a method is called"""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        key = method.__qualname__  # Get the qualified name of the method
        self._redis.incr(key)  # Increment count associated with the method
        return method(self, *args, **kwargs)  # Call the original method
    return wrapper


def call_history(method: Callable) -> Callable:
    """Decorator to store history of inputs and outputs for a function"""
    @functools.wraps(method)
    def wrapper(self, *args, **kwargs):
        # Create input and output list keys
        in_key = '{}:inputs'.format(method.__qualname__)
        out_key = '{}:outputs'.format(method.__qualname__)
        # Append input arguments to the input list
        self._redis.rpush(in_key, str(args))
        # Execute the wrapped function to retrieve the output
        output = method(self, *args, **kwargs)
        # Append the output to the output list
        self._redis.rpush(out_key, str(output))
        return output
    return wrapper


def replay(method: Callable) -> None:
    """Display the history of calls of a particular function"""
    function_name = method.__qualname__
    value = redis.Redis().get(function_name)
    try:
        value = int(value.decode('utf-8'))
    except Exception:
        value = 0
    # Create input and output list keys
    in_key = '{}:inputs'.format(function_name)
    out_key = '{}:outputs'.format(function_name)
    # Retrieve input and output lists from Redis

    inputs = Cache._redis.lrange(in_key, 0, -1)
    outputs = Cache._redis.lrange(out_key, 0, -1)

    print(f"{function_name} was called {value} times:")

    for in_arg, output in zip(inputs, outputs):
        print("{}(*{}) -> {}".format(
            method.__qualname__,
            in_arg.decode('utf-8'),
            output.decode('utf-8')
            ))
        print(f"{function_name}(*{in_arg.decode('utf-8')}) -> {output.decode('utf-8')}")



class Cache():
    """"Represents an object for storing data in a Redis data storage."""

    def __init__(self) -> None:
        """Initializes a Cache instance"""
        self._redis = redis.Redis()
        self._redis.flushdb(True)

    @call_history
    @count_calls
    def store(self, data: Union[str, bytes, int, float]) -> str:
        """Stores a value in a Redis data storage and returns the key"""
        random_key = str(uuid.uuid4())
        self._redis.set(random_key, data)
        return random_key

    def get(
            self, key: str, fn: Callable = None
            ) -> Union[str, bytes, int, float]:
        """Retrieves a value from a Redis data storage"""
        value = self._redis.get(key)
        return fn(value) if fn is not None else value

    def get_str(self, key: str) -> str:
        """Retrieves a string value from a Redis data storage"""
        return self.get(key, str)

    def get_int(self, key: str) -> int:
        """Retrieves an integer value from a Redis data storage"""
        return self.get(key, int)
