import redis
import requests
from typing import Callable

r = redis.Redis()


def cache_with_tracking(func: Callable) -> Callable:
    """
    Decorator that caches the result of a function
    """
    def wrapper(url: str) -> str:
        count_key = f"count:{url}"
        r.incr(count_key)
        cached_content = r.get(url)
        if cached_content:
            return cached_content.decode('utf-8')
        content = func(url)
        r.setex(url, 10, content)
        return content
    return wrapper


@cache_with_tracking
def get_page(url: str) -> str:
    """
    Fetches the HTML content of the given URL.
    """
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk"
    print(get_page(url))
    print(f"Access count: {r.get(f'count:{url}').decode('utf-8')}")
