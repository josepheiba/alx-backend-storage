import redis
import requests


r = redis.Redis()


def get_page(url: str) -> str:
    """
    Fetches the HTML content of the given URL and caches it for 10 seconds.
    Tracks the number of times the URL has been accessed.
    """
    count_key = f"count:{url}"
    r.incr(count_key)
    cached_content = r.get(url)
    if cached_content:
        return cached_content.decode('utf-8')
    response = requests.get(url)
    content = response.text
    r.setex(url, 10, content)
    return content


if __name__ == "__main__":
    url = "http://slowwly.robertomurray.co.uk"
    print(get_page(url))
    print(f"Access count: {r.get(f'count:{url}').decode('utf-8')}")
