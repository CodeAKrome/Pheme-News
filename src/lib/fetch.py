import requests
import threading
import time
import json


CACHE_FILE = "cache.json"
# 3 days in seconds
CACHE_DAYS = 60 * 60 * 24 * 3


def fetch(urls, timeout=30, cache_expiry=CACHE_DAYS):
    results = []
    thread_list = []
    url_cache = {}

    # Load cache from file
    try:
        with open(CACHE_FILE, "r") as f:
            url_cache = json.load(f)
    except FileNotFoundError:
        pass

    def fetch_url(url):
        result = {}
        try:
            # Check cache for data and expiry time
            if url in url_cache:
                data, expiry_time = url_cache[url]
                if time.time() < expiry_time:
                    result["status"] = "Cached"
                    result["url"] = url
                    result["data"] = data
                    return

            # Not in cache or cache expired, fetch data
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            data = response.content.decode("utf-8")

            # Add data to cache and write to file
            expiry_time = time.time() + cache_expiry
            url_cache[url] = (data, expiry_time)
            result["status"] = "Success"
            result["url"] = url
            result["data"] = data
        except requests.exceptions.RequestException as e:
            result["status"] = "Error"
            result["url"] = url
            result["data"] = str(e)
        finally:
            results.append(result)

    # Create threads to fetch urls in parallel
    for url in urls:
        t = threading.Thread(target=fetch_url, args=(url,))
        t.start()
        thread_list.append(t)

    # Wait for all threads to complete
    for t in thread_list:
        t.join()

    # Remove expired cache entries
    for url, (data, expiry_time) in list(url_cache.items()):
        if time.time() > expiry_time:
            del url_cache[url]
    with open(CACHE_FILE, "w") as f:
        json.dump(url_cache, f)

    return results


# === TEST ===


def selftest():
    base = "https://swapi.dev/api/people/"
    results = fetch([base + "1", "http://www.bogus.com", base + "2"])
    for res in results:
        print(f"{res}\n")


# === MAIN ===


if __name__ == "__main__":
    selftest()
