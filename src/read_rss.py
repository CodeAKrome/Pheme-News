#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
read_rss.py - Read RSS feeds from stdin and output articles in JSON format.
"""

import sys
import json
import re
import html

# from icecream import ic
from lib.util.decor import arrest
from dataclasses import dataclass, asdict, field

import feedparser
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.error
import socket

# aa aA0 htt
# language 2 letter code, name, ulr
VALID_RECORD = re.compile(
    r"^[a-z][a-z][\s\t]+[a-zA-Z][a-zA-Z0-9\-]*[\s\t]+https?:\/\/[^\t]*$"
)
FORMAT_ERROR = "Invalid input format. Should be 3 tab delimited columns: 2 letter language code, feed name (starting with a letter, then alphanumerics) and feed URL."
DEFAULT_TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"


@dataclass(slots=True)
class FeedSource:
    lang: str
    source: str
    url: str

    def __post_init__(self):
        if not VALID_RECORD.match(f"{self.lang}\t{self.source}\t{self.url}"):
            raise ValueError(FORMAT_ERROR)


@dataclass(slots=True)
class FeedRecord:
    lang: str
    source: str
    link: str
    title: str
    subtitle: str
    flavor: str = "rss"
    language: str = ""

    def __str__(self) -> str:
        return json.dumps(asdict(self))


@dataclass(slots=True)
class Article:
    lang: str
    source: str
    title: str
    link: str
    tags: list[str] = field(default_factory=list)
    flavor: str = "art"
    published: str = ""
    published_parsed: str = ""
    summary: str = ""
    media_content: [dict] = field(default_factory=list)
    media_thumbnail: [dict] = field(default_factory=list)

    def __str__(self) -> str:
        return json.dumps(asdict(self))


@dataclass(slots=True)
class Feed:
    source: str
    title: str
    description: str
    link: str
    kind: str = "rss"


#    articles: list[Article] = field(default_factory=list)


class ReadRss(BaseException):
    def __init__(self):
        pass

    @arrest([ValueError], "Invalid feed entry in input.")
    def validate_feed(self, line) -> FeedRecord:
        if line:
            if line[0] != "#" and VALID_RECORD.fullmatch(line):
                lang, source, url = line.split()
                if not (lang and source and url):
                    raise ValueError(FORMAT_ERROR)
                return FeedSource(lang, source, url)
            raise ValueError(f"{FORMAT_ERROR}\n{line}")
        raise ValueError("Blank line.")

    def html2txt(self, htmlstr: str) -> str:
        """Convert HTML to plain text"""
        # Replace HTML entities with their UTF-8 counterparts
        utf8_string = html.unescape(htmlstr)
        # Remove remaining HTML markup
        utf8_string = re.sub("\n", "", utf8_string)
        return re.sub("<[^<]+?>", "", utf8_string)

    @arrest([ValueError], "Couldn't read RSS feed, maybe 403 forbidden.")
    def read_rss(self, feed_rec: Feed, timeout=DEFAULT_TIMEOUT) -> FeedRecord:
        try:
            req = urllib.request.Request(
                feed_rec.url, headers={"User-Agent": USER_AGENT}
            )
            with urllib.request.urlopen(req, timeout=timeout) as response:
                data = response.read()
                records = feedparser.parse(data)
                # ic(records)
                rec = FeedRecord(
                    lang=feed_rec.lang,
                    source=feed_rec.source,
                    link=feed_rec.url,
                    title=records.feed.title,
                    subtitle=records.feed.subtitle,
                )

                if "language" in records.feed:
                    rec.language = records.feed.language
                print(rec)
                # print(dir(records))
                if records and len(records.entries) > 0:
                    for entry in records.entries:
                        # ic(entry)
                        article = Article(
                            lang=feed_rec.lang,
                            source=feed_rec.source,
                            title=entry.title,
                            link=entry.link,
                        )

                        # Main image entry. Detect other type of media.
                        if "media_content" in entry:
                            article.media_content = entry.media_content
                        if "media_thumbnail" in entry:
                            article.media_thumbnail = entry.media_thumbnail

                        if "summary" in entry:
                            article.summary = self.html2txt(entry.summary)
                        if "tags" in entry:
                            article.tags = [tag.term for tag in entry.tags]
                        # Fold fields updated and updated_parsed onto published and published_parsed
                        if "published" not in entry and "updated" in entry:
                            article.published = entry["updated"]
                        if (
                            "published_parsed" not in entry
                            and "updated_parsed" in entry
                        ):
                            article.published_parsed = entry["updated_parsed"]
                        if "published" in entry:
                            article.published = entry.published
                        if "published_parsed" in entry:
                            article.published_parsed = entry.published_parsed
                        print(article)

        except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout) as e:
            raise ValueError(f"Error fetching RSS feed from {feed_rec.url} {e}")

    def read(self):
        for i, line in enumerate(sys.stdin, start=1):
            line = line.strip()
            if not line:
                continue
            # Allow for comments if # is first character
            if line[0] == "#" or line.strip() == "":
                continue
            feed_rec = self.validate_feed(line)
            # print(f"{i}: {feed_rec}")
            feed = self.read_rss(feed_rec)

    # def (self, feed_record: Feed) -> Feed:


if __name__ == "__main__":
    processor = ReadRss()
    processor.read()
