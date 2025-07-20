#!/usr/bin/env python3
"""
Read RSS/Atom feed URLs from stdin, fetch the first three <link>s per feed,
print each article’s title + full paragraph text (<p>), and show a concise
summary at the end.  Every network call times out after 20 s.
"""

from __future__ import annotations

import socket
import sys
import textwrap
import time
from typing import NamedTuple, Optional, Tuple

import feedparser
import requests
from bs4 import BeautifulSoup

# ---------- global 20-second timeout ----------
socket.setdefaulttimeout(20)


class FeedStats(NamedTuple):
    total_articles: int
    loaded: int
    first_fail: Optional[str]


# ---------- helpers ----------
def clean(text: str) -> str:
    return " ".join(text.split())


def fetch_article(link: str) -> Tuple[str, Optional[str]]:
    """
    Return (paragraph_text, error).
    If error is None, paragraph_text is ready to print.
    """
    try:
        resp = requests.get(
            link,
            timeout=20,
            headers={"User-Agent": "RSS-Tester/1.0"},
        )
        resp.raise_for_status()
    except requests.exceptions.Timeout:
        return "", "Timeout after 20 s"
    except requests.exceptions.RequestException as exc:
        return "", str(exc)

    soup = BeautifulSoup(resp.text, "html.parser")
    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    return "\n\n".join(paragraphs), None


def process_feed(url: str) -> Tuple[str, FeedStats]:
    try:
        feed = feedparser.parse(url)
    except Exception as exc:
        return url, FeedStats(0, 0, f"Feed parse error: {exc}")

    title = clean(feed.feed.get("title") or url)
    entries = feed.entries[:3]  # only first 3
    total = len(entries)
    loaded = 0
    first_fail: Optional[str] = None

    for idx, entry in enumerate(entries, 1):
        link = entry.get("link")
        if not link:
            first_fail = first_fail or "Missing <link>"
            continue

        article_title = clean(entry.get("title") or "<no title>")
        print(f"\n>>> Feed: {title} — Article {idx}/3")
        print(f"Title: {article_title}")
        print(f"Link : {link}")
        print("-" * 72)

        paragraphs, err = fetch_article(link)
        if err:
            first_fail = first_fail or err
            print(f"ERROR: {err}\n")
            continue

        loaded += 1
        # Nicely wrap the text to 80 chars for readability
        print(textwrap.fill(paragraphs, width=80))
        print("-" * 72)

    return title, FeedStats(total, loaded, first_fail)


def main() -> None:
    feed_urls = [ln.strip() for ln in sys.stdin if ln.strip()]
    if not feed_urls:
        print("No URLs supplied on stdin.", file=sys.stderr)
        sys.exit(1)

    summary = {}
    start = time.time()

    for url in feed_urls:
        feed_title, stats = process_feed(url)
        summary[url] = (feed_title, stats)

    # ---------- final tally ----------
    print("\n" + "=" * 72)
    print("FINAL SUMMARY")
    print("=" * 72)
    for url, (title, stats) in summary.items():
        print(f"\n{title}")
        print(f"URL  : {url}")
        print(f"Attempted : {stats.total_articles}")
        print(f"Loaded OK : {stats.loaded}")
        if stats.first_fail:
            print(f"First fail: {stats.first_fail}")
    print(f"\nFinished in {time.time() - start:.1f} s.")


if __name__ == "__main__":
    main()