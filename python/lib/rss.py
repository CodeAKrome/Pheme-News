# -*- coding: utf-8 -*-
"""
Created on Fri May  5 17:37:20 2023

@author: kyle
"""

import feedparser
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.error
import socket

# Watch, this path may change if this is included from someplace else
from lib.chowda import html2txt


DEFAULT_TIMEOUT = 30


def rss_feeds(urls, timeout=DEFAULT_TIMEOUT):
    with ThreadPoolExecutor() as executor:
        future_to_url = {executor.submit(rss_feed, url, timeout): url for url in urls}
        results = []
        errors = []
        for future in as_completed(future_to_url):
            url = future_to_url[future]
            try:
                result = future.result()
                results.append(result)
            except Exception as e:
                errors.append((url, e))
    return (results, errors)


def rss_feed(url, timeout=DEFAULT_TIMEOUT):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as f:
            feed_data = f.read()
    except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout) as e:
        raise ValueError(f"Error fetching RSS feed from {url} {e}")
    feed = feedparser.parse(feed_data)
    items = []
    for entry in feed.entries:
        item = {
            "title": html2txt(entry.title),
            "link": entry.link,
            "summary": "",
            "published": "",
            "published_parsed": "",
        }
        if "tags" in entry:
            item["tags"] = entry["tags"]
        if "summary" in entry:
            item["summary"] = (html2txt(entry.summary))
        # Fold fields updated and updated_parsed onto published and published_parsed
        if "published" not in entry and "updated" in entry:
            entry["published"] = entry["updated"]
        if "published_parsed" not in entry and "updated_parsed" in entry:
            entry["published_parsed"] = entry["updated_parsed"]
        if "published" in entry:
            item["published"] = (entry.published,)
        if "published_parsed" in entry:
            item["published_parsed"] = (entry.published_parsed,)
        # In list, for some reason ...
        item["published"] = item["published"][0]
        item["published_parsed"] = item["published_parsed"][0]
        items.append(item)
    return {
        "url": url,
        "title": feed.feed.title,
        "description": feed.feed.description,
        "items": items,
    }


def pp_rss(results, errors):
    print("Results:")
    for result in results:
        print(result["title"])
        print(result["description"])
        for item in result["items"]:
            print(item["title"])
            print(item["link"])
            print(item["published"])
            print(item["summary"])
            print()
    print("Errors:")
    for url, error in errors:
        print(f"Error processing feed {url}: {error}")


def selftest():
    urls = [
        "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml",
        "https://www.theguardian.com/world/rss",
        "https://invalid-feed-url.com/feed.xml",
    ]
    results, errors = rss_feeds(urls, timeout=10)
    if errors:
        print(f"Feed errors: {errors}")
    pp_rss(results, errors)


if __name__ == "__main__":
    selftest()
