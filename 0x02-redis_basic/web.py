#!/usr/bin/env python3
"""
module contains function and decorator function
that caches requests in redis cache
"""
import redis
import requests
from functools import wraps


store = redis.Redis()


def url_cacher(method):
    """
    decorator function caches web requests
    """
    @wraps(method)
    def invoker(url):
        """
        function returns saves requests and returns cached requests
        """
        data = store.get(f"key:{url}")
        if data:
            return data.decode("utf-8")
        count = f"count:{url}"
        html = method(url)
        store.incr(count)
        store.set(url, html)
        store.expire(url, 10)
        return html
    return invoker


@url_cacher
def get_page(url: str) -> str:
    """
    function gets html content
    """
    return requests.get(url).text
