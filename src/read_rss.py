import sys
import json
import re
import html
from icecream import ic
from lib.util.decor import arrest
from dataclasses import dataclass, asdict, field

import feedparser
from concurrent.futures import ThreadPoolExecutor, as_completed
import urllib.error
import socket

VALID_RECORD = re.compile(r"^[a-zA-Z][a-zA-Z0-9\-]*\s+http:\/\/[^\t]*\.[a-zA-Z]*$")
FORMAT_ERROR = "Invalid input format. Should be 2 tab delimited columns: feed name (starting with a letter, then alphanumerics) and feed URL."
DEFAULT_TIMEOUT = 30


@dataclass(slots=True)
class FeedSource:
    source: str
    url: str

    def __post_init__(self):
        if not VALID_RECORD.match(f"{self.source}\t{self.url}"):
            raise ValueError(FORMAT_ERROR)


@dataclass(slots=True)
class FeedRecord:
    source: str
    link: str
    image: str
    language: str
    title: str
    subtitle: str
    flavor: str = "rss"

    def __str__(self) -> str:
        return json.dumps(asdict(self))


@dataclass(slots=True)
class Article:
    source: str
    title: str
    summary: str
    link: str
    published: str
    published_parsed: str
    tags: list[str] = field(default_factory=list)
    flavor: str = "art"

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
            if VALID_RECORD.fullmatch(line):
                source, url = line.split()
                if not (source and url):
                    raise ValueError(FORMAT_ERROR)
                return FeedSource(source, url)
            raise ValueError(f"{FORMAT_ERROR}\n{line}")
        raise ValueError("Blank line.")

    def html2txt(self, htmlstr: str) -> str:
        """Convert HTML to plain text"""
        # Replace HTML entities with their UTF-8 counterparts
        utf8_string = html.unescape(htmlstr)
        # Remove remaining HTML markup
        utf8_string = re.sub("\n", "", utf8_string)
        return re.sub("<[^<]+?>", "", utf8_string)

    def read_rss(self, feed_rec: Feed, timeout=DEFAULT_TIMEOUT) -> FeedRecord:
        try:
            with urllib.request.urlopen(feed_rec.url, timeout=timeout) as response:
                data = response.read()
                records = feedparser.parse(data)
                # ic(records)
                rec = FeedRecord(
                    source=feed_rec.source,
                    link=feed_rec.url,
                    title=records.feed.title,
                    subtitle=records.feed.subtitle,
                    language=records.feed.language,
                    image=records.feed.image['href'] if 'image' in records.feed else None,
                )
                print(rec)
                # print(dir(records))
                if records and len(records.entries) > 0:
                    for entry in records.entries:
                        article = Article(
                            source=records.feed.title,
                            title=entry.title,
                            summary=entry.summary,
                            link=entry.link,
                            published=entry.published,
                            published_parsed=str(entry.published_parsed),
                        )
                        
                        if 'summary' in entry:
                            article.summary = self.html2txt(entry.summary)
                        if 'tags' in entry:
                            article.tags = entry.tags
                        # Fold fields updated and updated_parsed onto published and published_parsed
                        if "published" not in entry and "updated" in entry:
                            article.published = entry["updated"]
                        if "published_parsed" not in entry and "updated_parsed" in entry:
                            article.published_parsed = entry["updated_parsed"]
                        if "published" in entry:
                            article.published = entry.published
                        if "published_parsed" in entry:
                            article.published_parsed = entry.published_parsed
                        print(article)

        except (urllib.error.HTTPError, urllib.error.URLError, socket.timeout) as e:
            raise ValueError(f"Error fetching RSS feed from {url} {e}")

    def read(self):
        for i, line in enumerate(sys.stdin, start=1):
            feed_rec = self.validate_feed(line.strip())
            print(f"{i}: {feed_rec}")
            feed = self.read_rss(feed_rec)

    # def (self, feed_record: Feed) -> Feed:


if __name__ == "__main__":
    processor = ReadRss()
    processor.read()
