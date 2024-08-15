#!/usr/bin/env python3
"""
Redis caching module
"""

import requests
import redis
import functools

# Create a Redis connection
redis_conn = redis.Redis()


def count_and_cache(url):
    """
    Decorator to count how many times a URL was accessed and cache the result.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(url):
            # Count how many times the URL was accessed
            count_key = f"count:{url}"
            redis_conn.incr(count_key)

            # Cache the result with an expiration time of 10 seconds
            cache_key = f"cache:{url}"
            cached_result = redis_conn.get(cache_key)
            if cached_result is not None:
                return cached_result.decode('utf-8')

            result = func(url)
            redis_conn.setex(cache_key, 10, result)
            return result

        return wrapper

    return decorator


@count_and_cache(url)
def get_page(url):
    """
    Get the HTML content of a particular URL.
    """
    response = requests.get(url)
    return response.text
