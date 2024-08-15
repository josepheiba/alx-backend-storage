#!/usr/bin/env python3
"""
0x02-redis_basic
"""
import requests
import redis
from typing import Callable
from functools import wraps
from time import sleep


redisInstance = redis.Redis()
redisInstance.flushdb()


def callsCount(method: Callable) -> Callable:
    """A decorator that takes a method callable argument
    that increments the callsCount."""

    @wraps(method)
    def incrCount(url: str) -> str:
        """A method that increments the numbers of requests
        done for a URL."""

        countKey = f"count:{url}"
        storageKey = f"storage:{url}"
        storageVal = redisInstance.get(storageKey)
        if storageVal:
            redisInstance.incr(countKey)
            return storageVal.decode("utf-8")
        call = method(url)
        redisInstance.setex(storageKey, 10, call)
        redisInstance.set(countKey, 1)
        return call

    return incrCount


@callsCount
def get_page(url: str) -> str:
    """A method that uses the requests module to obtain the HTML
    content of a particular URL and returns it."""
    try:
        response = requests.get(url).text
        return response
    except requests.RequestException as e:
        return


if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk"
    get_page(url)
    get_page(url)
    get_page(url)
    get_page(url)
    print(redisInstance.get(f"storage:{url}"))
    sleep(12)
    print(redisInstance.get(f"storage:{url}"))
