import time

"""Cache values for a given number of seconds to disk"""


# 7 * days == 604800
DEFAULT_LIFE = 604800
DEFAULT_CACHE = "cache.tsv"


def rcache(life: float = DEFAULT_LIFE, file: str = DEFAULT_CACHE):
    """Read cache file and drop expired entries on floor. Format: <timestamp>\t<item>\n"""
    try:
        with open(file, "r") as f:
            now = time.time()
            cache = {}
            for line in f:
                if line:
                    born, item = line.strip().split()
                    if now - float(born) <= life:
                        cache[item] = born
            return cache
    except FileNotFoundError:
        return {}


def wcache(cache, life: float = DEFAULT_LIFE, file: str = DEFAULT_CACHE):
    """Write non-expired cache items to disk"""
    if cache:
        with open(file, "w") as f:
            now = time.time()
            for item, born in cache.items():
                if now - float(born) <= life:
                    rec = f"{born}\t{item}\n"
                    f.write(rec)


def ccache(item, cache, life: float = DEFAULT_LIFE):
    """True if item in cache and not expired else false and make a cache entry with current time"""
    now = time.time()
    if item in cache:
        delta = now - cache[item]
        if delta < life:
            return True
    cache[item] = now
    return False
