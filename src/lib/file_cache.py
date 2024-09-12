import os
import json
import time

"""Cache keys and values with a TTL."""

class FileCache:
    def __init__(self, file_path, default_ttl_hours=72):
        self.file_path = file_path
        self.default_ttl_hours = default_ttl_hours
        self.cache = self._load_cache()

    def _load_cache(self):
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                return json.load(f)
        return {}

    def _save_cache(self):
        with open(self.file_path, 'w') as f:
            json.dump(self.cache, f)

    def put(self, key, value, ttl_hours=None):
        if ttl_hours is None:
            ttl_hours = self.default_ttl_hours
        expiration = time.time() + (ttl_hours * 3600)
        self.cache[key] = {'value': value, 'expiration': expiration}
        self._save_cache()

    def cached(self, key):
        if key in self.cache:
            if time.time() < self.cache[key]['expiration']:
                return True
            else:
                self.flush(key)
        return False

    def get(self, key):
        if self.cached(key):
            return self.cache[key]['value']
        return None

    def flush(self, key=None):
        if key:
            if key in self.cache:
                del self.cache[key]
        else:
            current_time = time.time()
            self.cache = {k: v for k, v in self.cache.items() if v['expiration'] > current_time}
        self._save_cache()
