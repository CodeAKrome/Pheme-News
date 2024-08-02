import json
import fileinput

import sys
import os
sys.path.append(os.path.abspath('../Decor'))
from Decor import Decor

import feedparser
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.error
import socket


from bs4 import BeautifulSoup
import html
import re

DEFAULT_TIMEOUT = 30

class Rss:
    def __init__(self):
        pass

    @staticmethod
    def truncurl(string: str) -> str:
        """Get rid of trailing stuff from article urls like promo and source tracking E.g. ?src=rss&campaign=foo"""
        if "#" in string:
            index = string.index("#")
            return string[:index]
        if "?" in string:
            index = string.index("?")
            return string[:index]
        else:
            return string

    @arrest([KeyError], "Missing url in feed record.")
    def feedrec(self, feed):
        """Print RSS feed record"""
        if "url" not in feed or feed["url"] == "":
            raise ValueError(f"Feed URL missing or empty.\n{feed}")
        else:
            rec = {
                "type": "rss",
                "source": "",
                "title": "",
                "description": "",
                "url": "",
            }
            for k in rec.keys():
                if k in feed:
                    rec[k] = feed[k]
            print(json.dumps(rec))

    @arrest([KeyError], "Missing link in article record.")
    def artrec(self, feed):
        """Print article record"""
        for art in feed["items"]:
            if "link" not in art or art["link"] == "":
                raise ValueError(f"Article URL missing or empty.\n{art}")
            else:
                rec = {
                    "type": "art",
                    "source": feed["source"],
                    "title": art["title"],
                    "summary": "",
                    "link": self.truncurl(art["link"]),
                    "published": art["published"],
                    "published_parsed": art["published_parsed"],
                }
                if "summary" in art:
                    rec["summary"] = art["summary"]
                if "tags" in art:
                    rec["tags"] = [tag["term"] for tag in art["tags"]]
                print(json.dumps(rec))

    @arrest([ValueError], "Couldn't get feed.")
    def proc(self, source: str, url: str):
        """Main processing"""
        feed = self.rss_feed(url)
        feed["source"] = source
        self.feedrec(feed)
        self.artrec(feed)

    @arrest([TypeError, ValueError], "Invalid feed entry in input.")
    def valid(self, line):
        """Feed url line input validation. Line is tab delim <source>\t<RSS url>"""
        source, url = line.split()
        source = str(source)
        if type(source) is not str:
            raise TypeError(f"Feed id type: {type(source)} must be string.")
        if "http" != url[:4]:
            raise ValueError(f"Feed URL: {url} must be of form http.")
        return source, url

    @arrest([TypeError], "I love trash -- Oscar T. Grouch.")
    def read(self):
        """Read lines from stdin. Should be source and url on lines."""
        ln = 0
        for line in fileinput.input():
            try:
                ln += 1
                source, url = self.valid(line.strip())
                self.proc(source, url)
            except Exception as e:
                log_error(f"stdin line: {ln} type: {type(e)} val: {e}\n[{line}]")

#----

    def rss_feeds(self, urls, timeout=DEFAULT_TIMEOUT):
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


    def rss_feed(self, url, timeout=DEFAULT_TIMEOUT):
        try:
            with urllib.request.urlopen(url, timeout=timeout) as f:
                feed_data = f.read()
        except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout) as e:
            raise ValueError(f"Error fetching RSS feed from {url} {e}")
        feed = feedparser.parse(feed_data)
        items = []
        for entry in feed.entries:
            item = {
                "title": self.html2txt(entry.title),
                "link": entry.link,
                "summary": "",
                "published": "",
                "published_parsed": "",
            }
            if "tags" in entry:
                item["tags"] = entry["tags"]
            if "summary" in entry:
                item["summary"] = self.html2txt(entry.summary)
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


    def pp_rss(self, results, errors):
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


#---

    def html2txt(self, htmlstr: str) -> str:
        """Convert HTML to plain text"""
        # Replace HTML entities with their UTF-8 counterparts
        utf8_string = html.unescape(htmlstr)
        # Remove remaining HTML markup
        utf8_string = re.sub("\n", "", utf8_string)
        return re.sub("<[^<]+?>", "", utf8_string)
#--->>

if __name__ == "__main__":
    processor = Rss()
    processor.read()
